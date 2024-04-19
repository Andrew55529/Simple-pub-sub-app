import pika
import json
import time
import random

def establish_connection():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            print("Connected")
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("Failed connect to RabbitMQ.")
            time.sleep(5)

def send_data(connection):
    channel = connection.channel()
    arguments = {
        'x-dead-letter-exchange': '',  
        'x-dead-letter-routing-key': 'data_dlq'  
    }   
    channel.queue_declare(queue='data', arguments=arguments)

    channel.queue_declare(queue='data_dlq')
    while True:
        try:
            data = {'value': random.randint(0, 9)} 
            channel.basic_publish(exchange='', routing_key='data', body=json.dumps(data))
            print("Sent data for calculation:", data)
            time.sleep(5)
        except pika.exceptions.AMQPConnectionError:
            print("Connection to RabbitMQ lost.")
            connection = establish_connection()

connection = establish_connection()
send_data(connection)