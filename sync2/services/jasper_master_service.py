from datetime import datetime, timedelta, timezone
import uuid
import logging
import pytz

from dateutil.tz import tzutc
logger = logging.getLogger(__name__)
from bson import ObjectId
import traceback
import json
from azure.servicebus import ServiceBusResourceNotFound
import time

DEFAULT_DATE = datetime(2010, 1, 1, 0, 0, 0, 0, tzinfo=tzutc())
MESSAGE_ICCID_BATCH_SIZE = 1
QUEUE_MESSAGE_BATCH_SIZE = 500
SLEEP_TIME = 1000
CARRIER_UPDATE_CYCLE_TIME = timedelta(minutes = 2)
CARRIER_UPDATE_ACTIVITY_TIME = timedelta(minutes = 1)
DEVICE_UPDATE_CYCLE_TIME = timedelta(hours = 4)
DEVICE_ACTIVITY_CYCLE_TIME = timedelta(hours = 1)
JASPER_UPDATE_LAG_TIME = timedelta(minutes = 5)

class JasperMasterService:

    def __init__(self, repositories, config, jasper_soap_api, ServiceBusClient, QueueClient, Message ):
        self.carrier_repo = repositories['carrier']
        self.device_repo = repositories['device']
        self.sync_repo = repositories['sync']
        self.jasper_soap_api = jasper_soap_api
        self.Message = Message
        self.ServiceBusClient = ServiceBusClient
        self.QueueClient = QueueClient
        self.config = config

    def run(self):
        while True:
            self.check_carriers()
            time.sleep(SLEEP_TIME)

    def check_carriers(self):
            # results = self.carrier_repo.get_carriers({'enabled': True, 'platform': 'jasper'})
            carrier = self.carrier_repo.get_carrier('5d6ec3d4bd6074001835b9ff')
            # for carrier in results['carriers']:
            # print(carrier)
            now = datetime.now(timezone.utc)
            config_activity = carrier.get('configActivity') or DEFAULT_DATE
            config_updated = carrier.get('configUpdated') or DEFAULT_DATE
            update_watermark = config_updated + CARRIER_UPDATE_ACTIVITY_TIME
            activity_watermark = config_activity + CARRIER_UPDATE_CYCLE_TIME
            ready_to_update = True #or update_watermark < now and activity_watermark < now
             
            if ready_to_update:
                logger.info(f"jasper carrier sync started - name: {carrier['name']} id: {carrier['id']} now: {now}")
                self.process_carrier(carrier, now, config_updated)


    def process_carrier(self, carrier, now, config_updated):
        try:
            update = {'configActivity': now}
            # self.carrier_repo.update_carrier(carrier['id'], update)

            queue_client = self.get_carrier_device_queue(carrier['id'])
            self.set_carrier_jasper_soap_api_credentials(carrier)

            carrier_paging = carrier['jasper']['paging']
            lagged_config_updated = config_updated - JASPER_UPDATE_LAG_TIME
            self.process_jasper_get_modified_terminals(carrier, carrier_paging, lagged_config_updated, now, queue_client)

           # self.process_device_usage_updates(carrier, now, queue_client)

           # update = {'configActivity': None, 'configUpdated': now, 'jasper.pageNumber':None}
           # self.carrier_repo.update_carrier(carrier['id'], update)

           # logger.info(f"jasper carrier sync complete - name: {carrier['name']} id: {carrier['id']} now:{now}")

        except Exception as ex:
            sync_error_entry = {
                'source': 'jasper_master_service',
                'accountId': ObjectId(carrier['accountId']),
                'carrierId': ObjectId(carrier['id']),
                'carrierName': carrier['name'],
                'platform': carrier['platform'],
                'type':'error',
                'logged': now,
                'message': str(ex),
                'trace': traceback.format_exc()
            }
           # self.sync_repo.insert_entry(sync_error_entry)
           # logger.error(f"jasper carrier sync error - name: {carrier['name']} id: {carrier['id']} start: {now}",
#                         exc_info=True, stack_info=True)

    def process_jasper_get_modified_terminals(self, carrier, carrier_paged, config_updated, now, queue_client):
        page_number = 1
        while True:
            update = {'configActivity': datetime.now(timezone.utc), 'jasper.pageNumber': page_number}
            # self.carrier_repo.update_carrier(carrier['id'], update)

            message_id = uuid.uuid4()
            config_updated =   datetime(2019, 9, 23)
            if carrier_paged:
                results = self.jasper_soap_api.get_modified_terminals(config_updated, message_id, page_number)
            else:
                results = self.jasper_soap_api.get_modified_terminals(config_updated, message_id)
            if not results or len(results['iccids']) < 1:
                break

            self.queue_device_details_requests(carrier, results['iccids'], now, queue_client)
            print(len(results['iccids']))
            page_number += 1
            break
            if not carrier_paged or page_number > results['pages']:
                break

    # def process_device_usage_updates(self, carrier, now, queue_client):
    #     update_watermark = now - DEVICE_UPDATE_CYCLE_TIME
    #     activity_watermark = now - DEVICE_ACTIVITY_CYCLE_TIME
    #     query = {
    #         'carrierId': ObjectId(carrier['id']),
    #         'jasper.status': { '$in': ['test_ready','activation_ready','activated'] },
    #         '$and': [
    #             {'$or': [
    #                     {'usageUpdated': {'$lt': update_watermark}},
    #                     {'usageUpdated': {'$exists': False}},
    #                     {'usageUpdated': None}
    #             ]},
    #             {'$or': [
    #                     {'usageActivity': {'$lt': activity_watermark}},
    #                     {'usageActivity': {'$exists': False}},
    #                     {'usageActivity': None},
    #                 ]}
    #         ]
    #     }

    #     results = self.device_repo.get_devices(query)
    #     if results['count'] > 0:
    #         iccids = [device['iccid'] for device in results['devices']]
    #         device_ids = [ObjectId(device['id']) for device in results['devices']]
    #         logger.info(f"jasper carrier device usage updates - name: {carrier['name']} id: {carrier['id']} "
    #             f"now:{now} update_watermark:{update_watermark} activity_watermark:{activity_watermark} " 
    #             f"iccids:{iccids} device_ids:{device_ids}")
    #         self.device_repo.update_devices({'_id': {'$in': device_ids}}, { '$set': {'usageActivity': now}})
    #         self.queue_device_details_requests(carrier, iccids, now, queue_client)

    def queue_device_details_requests(self, carrier, iccids, now, queue_client):
        json_messages = []
        iccid_index = 0
        while iccid_index < len(iccids):
            iccid_batch_size = MESSAGE_ICCID_BATCH_SIZE
            if (iccid_index + iccid_batch_size) > len(iccids):
                iccid_batch_size = len(iccids) - iccid_index

            json_message = {
                'accountId': carrier['accountId'],
                'carrierId': carrier['id'],
                'iccids': iccids[iccid_index: iccid_index+iccid_batch_size]
            }
            json_messages.append(json.dumps(json_message))
            print(json_messages)
            iccid_index += iccid_batch_size
        return
        msg_index = 0
        while msg_index < len(json_messages):
            message_batch_size = QUEUE_MESSAGE_BATCH_SIZE
            if (msg_index + message_batch_size) > len(json_messages):
                message_batch_size = len(json_messages) - msg_index
            messages = [self.Message(json_message.encode())
                        for json_message in json_messages[msg_index: msg_index+message_batch_size]]
            queue_client.send(messages)
            msg_index += message_batch_size

        logger.info(f"jasper carrier device usage queued - name: {carrier['name']} id: {carrier['id']} "
                    f"now:{now} iccids:{iccids}")

        sync_entry = {
            'source': 'jasper_master_service',
            'accountId': ObjectId(carrier['accountId']),
            'carrierId': ObjectId(carrier['id']),
            'carrierName': carrier['name'],
            'platform': carrier['platform'],
            'type': 'queued',
            'logged': now,
            'iccids': iccids
        }
        self.sync_repo.insert_entry(sync_entry)


    def get_carrier_device_queue_name(self, carrier_id):
        return f"jasper-carrier-{carrier_id}-device"


    def get_carrier_device_queue(self, carrier_id):
        queue_name = self.get_carrier_device_queue_name(carrier_id)
        service_bus_client = self.ServiceBusClient.from_connection_string(self.config.service_bus_connection_string)
        try:
            queue_client = service_bus_client.get_queue(queue_name)
        except ServiceBusResourceNotFound:
            service_bus_client.create_queue(queue_name, lock_duration=120)
            queue_client = service_bus_client.get_queue(queue_name)
        return queue_client


    # def get_queue_client(self, queue_name):
    #     queue_client = self.QueueClient.from_connection_string(self.config.service_bus_connection_string, queue_name)
    #     return queue_client


    def set_carrier_jasper_soap_api_credentials(self, carrier):
        self.jasper_soap_api.set_credentials(
            username=carrier['jasper']['credentials']['username'],
            password=carrier['jasper']['credentials']['password'],
            api_path=carrier['jasper']['credentials']['apiPath'],
            license_key=carrier['jasper']['credentials']['licenseKey'],
            carrier_id=carrier['id'],
            carrier_name=carrier['name'])









