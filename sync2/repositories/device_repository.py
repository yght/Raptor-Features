from bson import ObjectId
from bson.codec_options import CodecOptions
from pymongo import ReturnDocument
import repositories.utils as repo_utils

class DeviceRepository:

    def __init__(self, db):
        codec_options = CodecOptions(tz_aware=True)
        self.devices = db.get_collection('devices', codec_options=codec_options)

    def format_device_for_output(self, device):
        if device:
            repo_utils.rename_object_id(device)
            repo_utils.convert_to_string(device, ['accountId','carrierId'])
            if 'customerL1' in device:
                repo_utils.convert_to_string(device['customerL1'], ['accountId','planId'])
            if 'customerL2' in device:
                repo_utils.convert_to_string(device['customerL2'], ['accountId', 'planId'])

    def get_devices(self, query={}, skip = 0, limit = 1000000, sort = 'iccid asc' ):
        count = self.devices.count_documents(query, skip=skip, limit=limit)
        sort_tuple = repo_utils.process_sort_value(sort)
        devices = list(self.devices.find(query, skip=skip, limit=limit).sort(*sort_tuple))
        for device in devices: self.format_device_for_output(device)
        return {"count" : count, "limit": limit, "skip":skip, "sort": sort, "devices": devices}

    def get_device(self, device_id):
        device = self.devices.find_one({"_id": ObjectId(device_id)})
        self.format_device_for_output(device)
        return device

    def get_device_by_iccid(self, carrier_id, iccid):
        device = self.devices.find_one({"carrierId": ObjectId(carrier_id), "iccid":iccid})
        self.format_device_for_output(device)
        return device

    def create_device(self, device):
        repo_utils.convert_to_objectid(device, ['accountId','carrierId'])
        result = self.devices.insert_one(device)
        device['_id'] = result.inserted_id
        self.format_device_for_output(device)
        return device

    def update_device(self, device_id, update):
        query = {"_id": ObjectId(device_id)}
        changes = {"$set": update}
        device = self.devices.find_one_and_update(query, changes, return_document=ReturnDocument.AFTER)
        self.format_device_for_output(device)
        return device

    def update_devices(self, filter, update):
        result = self.devices.update_many(filter, update)
        return result

