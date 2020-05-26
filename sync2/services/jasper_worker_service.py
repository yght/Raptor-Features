from datetime import datetime, timedelta, timezone
import uuid
import logging
logger = logging.getLogger(__name__)
from bson import ObjectId
import traceback
import json
import time
from azure.servicebus import ServiceBusResourceNotFound
from apis.jasper_soap_api import JasperSoapApiError

QUEUE_MESSAGE_BATCH_SIZE = 500
QUEUE_FETCH_BATCH_SIZE = 100

class JasperWorkerService:

    def __init__(self, repositories, jasper_soap_api, config, ServiceBusClient, QueueClient, Message):
        self.audit_repo = repositories['audit']
        self.carrier_repo = repositories['carrier']
        self.device_repo = repositories['device']
        self.sync_repo = repositories['sync']
        self.usage_repo = repositories['usage']
        self.jasper_soap_api = jasper_soap_api
        self.Message = Message
        self.ServiceBusClient = ServiceBusClient
        self.QueueClient = QueueClient
        self.config = config

    def run(self):
        self.process_carriers()

    def process_carriers(self):
        while True:
            # results = self.carrier_repo.get_carriers({'enabled': True, 'platform': 'jasper'})
            # for carrier in results['carriers']:
            #       self.process_carrier_queue(carrier)
            carrier = self.carrier_repo.get_carrier('5d6ec3d4bd6074001835b9ff')
            self.process_carrier_queue(carrier)

    def process_carrier_queue(self, carrier):
        try:
            now = datetime.now(timezone.utc)
            # logger.info(f"jasper worker process_carrier_queue - name: {carrier['name']} id: {carrier['id']} now: {now}")

            queue_client = self.get_carrier_device_queue(carrier['id'])
            if not queue_client:
                # logger.info(
                #     "jasper worker process_carrier_queue no queue found - name: {carrier['name']} id: {carrier['id']} now: {now}")
                return

            self.set_carrier_jasper_soap_api_credentials(carrier)
            with queue_client.get_receiver() as queue_receiver:
                for i in range(QUEUE_FETCH_BATCH_SIZE):
                    messages = queue_receiver.fetch_next(timeout=1)
                    # print('FETCHEDDDDDDDDDDDDDDD')
                    if messages:
                        for message in messages:
                            # logger.info(
                            #     f"jasper worker process_carrier_queue - name: {carrier['name']} id: {carrier['id']} "
                            #     f"now: {now} - {message}"
                            # )
                            self.process_queue_message(carrier, now, message)
                    else:
                        break

        except Exception as ex:
            print(ex)
            print('EROROROROROR')
            exit(0)
            sync_error_entry = {
                'source': 'jasper_worker_service',
                'accountId': ObjectId(carrier['accountId']),
                'carrierId': ObjectId(carrier['id']),
                'carrierName': carrier['name'],
                'platform': carrier['platform'],
                'type': 'error',
                'logged': now,
                'message': str(ex),
                'trace': traceback.format_exc()
            }
            self.sync_repo.insert_entry(sync_error_entry)
            logger.error(
                f"jasper carrier worker process_carrier_queue error - name: {carrier['name']} id: {carrier['id']} start: {now}",
                exc_info=True, stack_info=True)

    def process_queue_message(self, carrier, now, message):
        # print('MEASSAGE')
        # print(message)
        json_message = json.loads(str(message))
        iccids = ['89011703278392134295', '89011703278392134287'] #json_message['iccids']
        for iccid in iccids:
            message_id = uuid.uuid4()
            try:
                details = self.jasper_soap_api.get_terminal_details([iccid], message_id)
                self.update_devices_from_message(carrier, now, details)
                #message.complete()
            except JasperSoapApiError as jsae:
                sync_error_entry = {
                    'source': 'jasper_worker_service',
                    'accountId': ObjectId(carrier['accountId']),
                    'carrierId': ObjectId(carrier['id']),
                    'carrierName': carrier['name'],
                    'platform': carrier['platform'],
                    'type': 'error',
                    'iccid': iccid,
                    'logged': now,
                    'message': jsae.message,
                    'fault': jsae.fault,
                    'content': jsae.content
                }
                self.sync_repo.insert_entry(sync_error_entry)
                logger.error(
                   f"kore carrier worker process_queue_message api error - name: {carrier['name']} "
                   f"id: {carrier['id']} iccids: {iccids} message: {jsae.message} content:{jsae.content}")

    def update_includes_usage_change(self, update):
        return (
            'jasper.monthToDateUsage' in update or
            'jasper.monthToDateDataUsage' in update or
            'jasper.monthToDateSMSUsage' in update or
            'jasper.monthToDateVoiceUsage' in update
        )

    def update_devices_from_message(self, carrier, now, details):
        for detail in details:
            device = self.device_repo.get_device_by_iccid(carrier_id=carrier['id'], iccid=detail['iccid'])
            if not device:
               
                print('NOT INCLUDED')
                device = self.get_device_create_doc(carrier, detail, now)
                create_result = self.device_repo.create_device(device)
                device['id'] = str(create_result['id'])
                #logger.info(f"jasper worker device created - {device}")
                print(device)
                self.insert_device_create_audit_entry(carrier, device)
                self.insert_device_usage_entry(carrier, device)
            else:
                # print('Already ')
                print(device['iccid'])
                # update = self.get_device_update_doc(device, detail, now)
                # if len(update.keys()) > 4:
                #     device = self.device_repo.update_device(str(device['id']), update)
                #     self.insert_device_update_audit_entry(carrier, device, update)
                #     if self.update_includes_usage_change(update):
                #         self.insert_device_usage_entry(carrier, device)

            # sync_entry = {
            #     'carrierId': ObjectId(carrier['id']),
            #     'carrierName': carrier['name'],
            #     'accountId': ObjectId(device['accountId']),
            #     'platform': device['platform'],
            #     'source': 'jasper_worker_service',
            #     'type': 'updated',
            #     'logged': now,
            #     'iccids': [detail['iccid'] for detail in details]
            # }
            # self.sync_repo.insert_entry(sync_entry)

    def get_device_create_doc(self, carrier, detail, now):
        doc = {
            'accountId': carrier['accountId'],
            'platform': 'jasper',
            'carrierId': carrier['id'],
            'carrierName': carrier['name'],
            'configUpdated': now,
            'created': now,
            'createdBy': 'system',
            'custom': {},
            'customerL1': None,
            'customerL2': None,
            'iccid': detail['iccid'],
            'imei': detail['imei'],
            'imsi': detail['imsi'],
            'jasper': self.get_jasper_fields_for_device(detail),
            'msisdn': detail['msisdn'],
            'mtdData': detail['monthToDateUsage'],
            'searchUpdated': None,
            'updated': now,
            'updatedBy': 'system',
            'usageActivity': None,
            'usageUpdated': now
        }
        self.set_device_custom_fields(doc, doc['jasper'])
        return doc

    def get_device_update_doc(self, current_device, detail, now):
        update = {
            'configUpdated': now,
            'searchUpdated': None,
            'updated': now,
            'updatedBy': 'system'
        }
        jasper_fields = self.get_jasper_fields_for_device(detail)
        for key in jasper_fields:
            if current_device['jasper'][key] != jasper_fields[key]:
                update[f'jasper.{key}'] = jasper_fields[key]
        return update

    def set_device_custom_fields(self, device, jasper):
        device['custom']['field1'] = jasper['custom1']
        device['custom']['field2'] = jasper['custom2']
        device['custom']['field3'] = jasper['custom3']
        device['custom']['field4'] = jasper['custom4']
        device['custom']['field5'] = jasper['custom5']
        device['custom']['field6'] = jasper['custom6']
        device['custom']['field7'] = jasper['custom7']
        device['custom']['field8'] = jasper['custom8']
        device['custom']['field9'] = jasper['custom9']
        device['custom']['field10'] = jasper['custom10']

    def get_jasper_fields_for_device(self, detail):
        return {
            'accountId': detail['accountId'],
            'communicationPlan': '',
            'ctdSessionCount': detail['ctdSessionCount'],
            'custom1': detail['custom1'],
            'custom2': detail['custom2'],
            'custom3': detail['custom3'],
            'custom4': detail['custom4'],
            'custom5': detail['custom5'],
            'custom6': detail['custom6'],
            'custom7': detail['custom7'],
            'custom8': detail['custom8'],
            'custom9': detail['custom9'],
            'custom10': detail['custom10'],
            'customer': '',
            'dateActivated': detail['dateActivated'],
            'dateAdded': detail['dateAdded'],
            'dateModified': detail['dateModified'],
            'dateShipped': detail['dateShipped'],
            'fixedIpAddress': detail['fixedIpAddress'],
            'modem': detail['modem'],
            'monthToDateUsage': detail['monthToDateUsage'],
            'monthToDateDataUsage': detail['monthToDateDataUsage'],
            'monthToDateSMSUsage': detail['monthToDateSMSUsage'],
            'monthToDateVoiceUsage': detail['monthToDateVoiceUsage'],
            'ratePlan': detail['ratePlan'],
            'status': self.convert_from_jasper_soap_status(detail['status']),
            'terminalId': detail['terminalId'],
        }

    def convert_from_jasper_soap_status(self, status):
        return status.replace('_NAME', '').lower()

    def insert_device_create_audit_entry(self, carrier, device):
        audit_entry = {
            'type': 'device',
            'action': 'create',
            'userId': 'system',
            'logged': device['created'],
            'accountId': ObjectId(device['accountId']),
            'carrierId': ObjectId(device['carrierId']),
            'platform': carrier['platform'],
            'deviceId': ObjectId(device['id']),
            'iccid': device['iccid'],
            'info': device
        }
        self.audit_repo.insert_entry(audit_entry)

    def insert_device_update_audit_entry(self, carrier, device, update):
        audit_update = {}
        for key in update:
            if "jasper." in key:
                splits = key.split('jasper.')
                if 'jasper' not in audit_update:
                    audit_update['jasper'] = {}
                audit_update['jasper'][splits[1]] = update[key]
            else:
                audit_update[key] = update[key]

        audit_entry = {
            'type': 'device',
            'action': 'update',
            'userId': 'system',
            'logged': device['updated'],
            'accountId': ObjectId(device['accountId']),
            'carrierId': ObjectId(device['carrierId']),
            'platform': carrier['platform'],
            'deviceId': ObjectId(device['id']),
            'iccid': device['iccid'],
            'info': audit_update
        }
        self.audit_repo.insert_entry(audit_entry)

    def insert_device_usage_entry(self, carrier, device):
        usage_entry = {
            'accountId': ObjectId(device['accountId']),
            'carrierId': ObjectId(device['carrierId']),
            'platform': carrier['platform'],
            'deviceId': ObjectId(device['id']),
            'iccid': device['iccid'],
            'logged': device['updated'],
            'mtdData': device['jasper']['monthToDateDataUsage'],
            'mtdSMS': device['jasper']['monthToDateSMSUsage'],
            'mtdVoice': device['jasper']['monthToDateVoiceUsage']
        }
        self.usage_repo.insert_entry(usage_entry)
        # logger.info(f"jasper worker device usage - {usage_entry}")
        usage_update = {'mtdData': usage_entry['mtdData'],'usageUpdated': device['updated'], 'usageActivity': None}
        self.device_repo.update_device(str(device['id']), usage_update)

    def get_carrier_device_queue_name(self, carrier_id):
        return f"jasper-carrier-5d6ec3d4bd6074001835b9ff-device_old"

    def get_carrier_device_queue(self, carrier_id):
        try:
            queue_name = self.get_carrier_device_queue_name(carrier_id)
            service_bus_client = self.ServiceBusClient.from_connection_string(self.config.service_bus_connection_string)
            queue_client = service_bus_client.get_queue(queue_name)
            return queue_client
        except ServiceBusResourceNotFound:
            return None

    def set_carrier_jasper_soap_api_credentials(self, carrier):
        self.jasper_soap_api.set_credentials(
            username=carrier['jasper']['credentials']['username'],
            password=carrier['jasper']['credentials']['password'],
            api_path=carrier['jasper']['credentials']['apiPath'],
            license_key=carrier['jasper']['credentials']['licenseKey'],
            carrier_id=carrier['id'],
            carrier_name=carrier['name'])