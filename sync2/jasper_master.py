from utils import config
import requests
from apis import JasperSoapApi
from repositories import CarrierRepository, DeviceRepository, SyncRepository
from azure.servicebus import ServiceBusClient, QueueClient, Message
from utils import config
from pymongo import MongoClient
from services import JasperMasterService
import datetime
import traceback

def main():
    client = MongoClient(config.mongo_uri)
    db = client[config.mongo_db]


    repositories = {
        "carrier" : CarrierRepository(db),
        "device" : DeviceRepository(db),
        "sync" : SyncRepository(db),

    }

    jasper_soap_api = JasperSoapApi(requests)
    jasper_master_service = JasperMasterService(
        repositories,
        config,
        jasper_soap_api,
        ServiceBusClient,
        QueueClient,
        Message
    )

    jasper_master_service.run()



if __name__ == "__main__":
    main()