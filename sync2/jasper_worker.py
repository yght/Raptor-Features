from utils import config
import requests
from apis import JasperSoapApi
from repositories import AuditRepository, CarrierRepository, DeviceRepository, SyncRepository, UsageRepository
from azure.servicebus import ServiceBusClient, QueueClient, Message
from utils import config
from pymongo import MongoClient
from services import JasperWorkerService
import datetime
import traceback

from soap_api import SoapTestApis
import logging
logging.basicConfig(level=logging.INFO)
uamqp_logger = logging.getLogger("uamqp")
uamqp_logger.setLevel(level=logging.ERROR)
logger = logging.getLogger(__name__)

def main():
    logger.info(f"jasper_worker starting")
    client = MongoClient(config.mongo_uri)
    db = client[config.mongo_db]

    repositories = {
        "audit": AuditRepository(db),
        "carrier": CarrierRepository(db),
        "device": DeviceRepository(db),
        "sync": SyncRepository(db),
        "usage": UsageRepository(db)
    }

    jasper_soap_api = JasperSoapApi(requests)

    jasper_worker_service = JasperWorkerService(
        repositories,
        jasper_soap_api,
        config,
        ServiceBusClient,
        QueueClient,
        Message)

    logger.info("jasper_worker running")


    soapTest = SoapTestApis(repositories,
        jasper_soap_api,
        config,
        ServiceBusClient,
        QueueClient,
        Message)
    try:
      jasper_worker_service.run()
    #   result1= soapTest.get_device_details('89011703278454940910', '5d6ec3d4bd6074001835b9ff')
    #   result2 = soapTest.get_modified_terminals('5d6ec3d4bd6074001835b9ff')
      print(result1, result2)

    except Exception as ex:
        sync_error_entry = {
            'source': 'jasper_worker',
            'platform': 'jasper',
            'type': 'error',
            #'logged': datetime.utcnow(),
            'error': {'message': str(ex), 'trace': traceback.format_exc()}
        }
        # repositories['sync'].insert_entry(sync_error_entry)
        logger.error(f"jasper_worker sync error",
                     exc_info=True, stack_info=True)

if __name__ == "__main__":
    main()





