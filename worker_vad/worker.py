import pika
import time
from DAO.connection import Connection
import os
import multiprocessing
import json
import logging
from vad.main import main
LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


def callback(ch, method, properties, body):
    try:
        print(" [x] Received %r" % body, flush=True)
        oid = json.loads(body)['oid']
        conn = Connection()
        file = conn.get_file(oid=oid)
        try:

            data = main(file.tobytes())
            print(data,  flush=True)

        except Exception as e:
            print(e, flush=True)

        conn = Connection()
        try:
            conn.insert_jobs('vad', 'done', bytes(json.dumps(data)))
        except:
            LOGGER.info('Error Inserting')
            conn.insert_jobs('vad', 'done', bytes(json.dumps(data)))

    except:
        logging.info('error')

    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume():
    logging.info('[x] start consuming')
    success = False
    while not success:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=os.environ['QUEUE_SERVER']))
            channel = connection.channel()
            success = True
        except:
            pass

    channel.queue_declare(queue='vad', durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='vad', on_message_callback=callback)

    channel.start_consuming()

consume()
'''
workers = int(os.environ['NUM_WORKERS'])
pool = multiprocessing.Pool(processes=workers)
for i in range(0, workers):
    pool.apply_async(consume)

# Stay alive
try:
    while True:
        continue
except KeyboardInterrupt:
    print(' [*] Exiting...')
    pool.terminate()
    pool.join()'''