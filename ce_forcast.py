import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import logging
import json
import os
from datetime import datetime, timedelta
import calendar
import csv

#email lib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

my_session = boto3.session.Session()
my_region = my_session.region_name

def lambda_handler(event, context):
    
    total_forecast, forecast_dates = forecast()
    mydict = last_month_spend()
    # name of csv file
    filename = "/tmp/spend.csv"
    make_csv(mydict, filename)
    summary = f'Total forecast is {total_forecast} for {forecast_dates["Start"]} to {forecast_dates["End"]}'
    sendReport(filename, summary)


def forecast():

    start_date = datetime.today()
    end_date = datetime(start_date.year,start_date.month,1) + timedelta(days=calendar.monthrange(start_date.year,start_date.month)[1] - 1)
    client = boto3.client('ce')
    response = client.get_cost_forecast(
    TimePeriod={
        'Start': start_date.strftime('%Y-%m-%d'),
        'End': end_date.strftime('%Y-%m-%d')
    },
    Metric='NET_UNBLENDED_COST',
    Granularity='MONTHLY')

    total_forecast = response['Total']['Amount']
    forecast_dates = response['ForecastResultsByTime'][0]['TimePeriod']
    return(total_forecast, forecast_dates)

def last_month_spend():
    start_date = datetime.today().replace(day=1)
    end_date = datetime.today()
    client = boto3.client('ce')
    response = client.get_cost_and_usage(
        Metrics=['NET_UNBLENDED_COST'],
        TimePeriod={
            'Start': start_date.strftime('%Y-%m-%d'),
            'End': end_date.strftime('%Y-%m-%d')
        },
        Granularity='MONTHLY',
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'LINKED_ACCOUNT'
            },
        ]
    )
    #print(response['ResultsByTime'][0]['Groups'])
    mydict = []
    for account_data in response['ResultsByTime'][0]['Groups']:

        account = account_data['Keys'][0]
        spend = account_data['Metrics']['NetUnblendedCost']['Amount']
        print(f'{account}, {spend}')

        mydict.append({'Linked account name': account, 'Linked account total': spend})
    return mydict

def make_csv(mydict, filename):
    # headers
    fields =['Linked account name','Linked account total']
       
    # writing to csv file
    with open(filename, 'w') as csvfile:
        # creating a csv dict writer object
        writer = csv.DictWriter(csvfile, fieldnames=fields)
    
        # writing headers (field names)
        writer.writeheader()
    
        # writing data rows
        writer.writerows(mydict)
    
# Send report via SES
def sendReport(filename, summary):
    to_emails = [os.environ['RECEIVER']]
    my_session = boto3.session.Session()
    my_region = my_session.region_name
    ses = boto3.client('ses', region_name=my_region)
    msg = MIMEMultipart()
    msg['Subject'] = 'Weekly report'
    msg['From'] = os.environ['SENDER']
    msg['To'] = to_emails[0]

    # what a recipient sees if they don't use an email reader
    msg.preamble = 'Multipart message.\n'

    # the message body
    part = MIMEText(summary)
    msg.attach(part)

    # the attachment
    part = MIMEApplication(open(filename, 'rb').read())
    part.add_header('Content-Disposition', 'attachment', filename=filename)
    msg.attach(part)

    result = ses.send_raw_email(
        Source=msg['From'],
        Destinations=to_emails,
        RawMessage={'Data': msg.as_string()}
    )                                                                                                       
    # and send the message
    print(result)

lambda_handler(None, None)