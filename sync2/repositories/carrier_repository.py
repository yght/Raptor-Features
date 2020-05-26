from pymongo import ReturnDocument
import repositories.utils as repo_utils
from bson import ObjectId
from bson.codec_options import CodecOptions
from bson.raw_bson import RawBSONDocument


class CarrierRepository:
    def __init__(self, db):
        self.carriers = db.get_collection('carriers')

    
    def format_carrier_for_output(self, carrier):
        if carrier:
            repo_utils.rename_object_id(carrier)
            repo_utils.convert_to_string(carrier, ['accountId'])

    def get_carriers(self, query = {}, skip = 0, limit = 1000000, sort = 'id asc' ):
        count = self.carriers.count_documents(query, skip=skip, limit=limit)
        sort_tuple=repo_utils.process_sort_value(sort)
        carriers = list(self.carriers.find(query, skip=skip, limit=limit).sort(*sort_tuple))
        for carrier in carriers: self.format_carrier_for_output(carrier)
        return {"count" : count, "limit": limit, "skip":skip, "sort": sort, "carriers": carriers}

    def get_carrier(self, carrier_id):
        carrier = self.carriers.find_one({"_id": ObjectId(carrier_id)})
        self.format_carrier_for_output(carrier)
        return carrier

    def update_carrier(self, carrier_id, update):
        query = {"_id": ObjectId(carrier_id)}
        changes = {"$set": update}
        carrier = self.carriers.find_one_and_update(query, changes, return_document=ReturnDocument.AFTER)
        self.format_carrier_for_output(carrier)
        return carrier