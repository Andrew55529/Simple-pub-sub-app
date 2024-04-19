import pika
import json
import time
from datetime import datetime

file_path = '/app/result/data_results.txt'

def save_to_file(data, result):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(file_path, 'a') as file:
        file.write(f"{current_time}  Data: {data}, Result: {result}\n")

def establish_connection():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            print("Connected")
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("Failed connect to RabbitMQ.")
            time.sleep(5)

def callback(ch, method, properties, body):
    data = json.loads(body)
    print("Received data:", data)

    try:
        if data['value'] > 7:
            raise ValueError("Value is greater than 8")
        result = data['value'] * 20 
        print("Result:", result)
        save_to_file(data,result)
    except Exception as e:
        print("Error processing data:", e)
        ch.basic_nack(delivery_tag=method.delivery_tag,requeue=False)
        return
    ch.basic_ack(delivery_tag=method.delivery_tag)

def consume_data(connection):
    channel = connection.channel()

    arguments = {
        'x-dead-letter-exchange': '',  
        'x-dead-letter-routing-key': 'data_dlq'  
    }   
    channel.queue_declare(queue='data', arguments=arguments)

    channel.queue_declare(queue='data_dlq')

    channel.basic_consume(queue='data', on_message_callback=callback)

    print('Waiting messages')
    try:
        channel.start_consuming()
    except pika.exceptions.AMQPConnectionError:
        print("Connection to RabbitMQ lost.")
        connection = establish_connection()
        consume_data(connection)

connection = establish_connection()
consume_data(connection)
