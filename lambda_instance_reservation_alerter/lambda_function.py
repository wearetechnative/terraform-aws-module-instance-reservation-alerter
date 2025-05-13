import boto3
from datetime import datetime
from pytz import timezone
import os
import json
import traceback

rds_client      = boto3.client('rds')
redshift_client = boto3.client('redshift')
ec2_client      = boto3.client('ec2')
sns_client      = boto3.client('sns')
sts_client      = boto3.client('stss')
sqs_client      = boto3.client('sqs')

client_name           = os.environ['CLIENT_NAME']
account_name          = os.environ['ACCOUNT_NAME']
notification_endpoint = os.environ['NOTIFICATION_ENDPOINT']

def get_reserved_instances():
    # Get reservations
    
    reservations_dict = {'Reservations': []}

    rds_response      = rds_client.describe_reserved_db_instances()
    redshift_response = redshift_client.describe_reserved_nodes()
    ec2_response      = ec2_client.describe_reserved_instances()

    # Get RedShift instances
    for reserved_node in redshift_response["ReservedNodes"]:

        if reserved_node['State'] == 'active':

            reservations_dict['Reservations'].extend(
                    [{  'service'       : 'RedShift',
                        'reservation_id': reserved_node['ReservedNodeId'],
                        'offering_id'   : reserved_node['ReservedNodeOfferingId'],
                        'node_type'     : reserved_node['NodeType'],
                        'start_time'    :reserved_node['StartTime']
                    }]
            )

    # Get RDS instances
    for reserved_db_instance in rds_response['ReservedDBInstances']:

        if reserved_db_instance['State'] == 'active':
            
            reservations_dict['Reservations'].extend(
                [{
                    'service'       : 'RDS',
                    'reservation_id': reserved_db_instance['ReservedDBInstanceId'],
                    'offering_id'   : reserved_db_instance['ReservedDBInstancesOfferingId'],
                    'node_type'     : reserved_db_instance['DBInstanceClass'],
                    'start_time'    :reserved_db_instance['StartTime'],
                }]
            )

    # Get EC2 instances
    for reserved_ec2_instance in ec2_response["ReservedInstances"]:
        
        if reserved_ec2_instance['State'] == 'active':

            reservations_dict['Reservations'].extend(
                [{
                    'service'       : 'EC2',
                    'reservation_id': reserved_db_instance['ReservedInstancesId'],
                    'offering_id'   : reserved_db_instance['OfferingType'],
                    'node_type'     : reserved_db_instance['InstanceType'],
                    'start_time'    :reserved_db_instance['Start'],
                }]
            )


    return reservations_dict

def publish_sns_message(reservations, current_date, account_id, account_name, notification_endpoint):

    for reservation in reservations['Reservations']:

        # Calculate how many days left.
        time_left = current_date - reservation['start_time']

        if time_left == 7:
            priority = "P2"
        elif time_left == 1:
            priority = "P1"
        else:
            print(f'{reservation["service"]} Reservation expiring in {time_left.days} days.')
            exit()

        sns_client.publish(
            TopicArn= notification_endpoint,
            Subject=f'{priority} Warning {reservation["service"]} Reservation expiring in {time_left.days} days.',
            Message=f"""
RESERVATION EXPIRATION NOTICE

Service: {reservation["service"]}
Reservation ID: {reservation["reservation_id"]}
Instance Type: {reservation["node_type"]}
Days Remaining: {time_left.days}
Expiration Date: {(current_date + time_left).strftime('%Y-%m-%d')}
AWS Account ID: {account_id}
AWS Account Name: {account_name}

ACTION REQUIRED:
This reserved instance will convert to on-demand pricing after expiration, 
resulting in potential cost increase.
"""
        )


def publish_sqs_message(reservations, current_date, account_id, client_name, account_name, notification_endpoint):

    for reservation in reservations['Reservations']:
        # Calculate how many days left.
        time_left = current_date - reservation['start_time']

        if time_left == 7:
            priority = "P2"
        elif time_left == 1:
            priority = "P1"
        else:
            print(f'{reservation["service"]} Reservation expiring in {time_left.days} days.')
            exit()

        message = {
            'direct_message': True,
            'subject': f'Warning {reservation["service"]} Reservation expiring in {time_left.days} days.',
            'message': f"""
RESERVATION EXPIRATION NOTICE

Service: {reservation["service"]}
Reservation ID: {reservation["reservation_id"]}
Instance Type: {reservation["node_type"]}
Days Remaining: {time_left.days}
Expiration Date: {(current_date + time_left).strftime('%Y-%m-%d')}

ACTION REQUIRED:
This reserved instance will convert to on-demand pricing after expiration, 
resulting in potential cost increase.
""",
            'account_id': account_id,
            'alias': f'{account_id}-reservation-{reservation["reservation_id"]}',
            'client_name': client_name,
            'sla': '8x5',
            'account_name': account_name,
            'priority': priority
        }


        # Message must be string to be forwarded or else you will get a type error.
        message_json = json.dumps(message)

        return sqs_client.send_message(
                QueueUrl=notification_endpoint,
                MessageBody=message_json,
            )


def lambda_handler(event, context):
    try:
        current_date = datetime.now(timezone('UTC'))
        sts_response = sts_client.get_caller_identity()
        account_id   = sts_response['Account']

        reservation_details = get_reserved_instances()

        if notification_endpoint.startswith("https://sqs"):
            publish_sqs_message(reservation_details, current_date, account_id, client_name, account_name, notification_endpoint)
        elif notification_endpoint.startswith("arn:aws:sns"):
            publish_sns_message(reservation_details, current_date, account_id, account_name, notification_endpoint)
    except Exception as e:
        error_traceback = traceback.format_exc()

        exception_message = {
            'subject': f'There is an error with the Instance Reservation Alerter Lambda in the {account_name} {account_id}.',
            'message': f'{error_traceback}'
            }
        
        print(exception_message)
        raise
