import repositories.utils as repo_utils
from bson.codec_options import CodecOptions

class AuditRepository:

    def __init__(self, db):
        codec_options = CodecOptions(tz_aware=True)
        self.audit = db.get_collection('audit', codec_options=codec_options)

    def format_entry_for_output(self, entry):
        if entry:
            repo_utils.rename_object_id(entry)
            repo_utils.convert_to_string(entry, ["accountId","carrierId"])

    def get_entries(self, query={}, skip = 0, limit = 1000000, sort = 'logged asc' ):
        count = self.audit.count_documents(query, skip=skip, limit=limit)
        sort_tuple = repo_utils.process_sort_value(sort)
        entries = list(self.audit.find(query, skip=skip, limit=limit).sort(*sort_tuple))
        for entry in entries: self.format_entry_for_output(entry)
        return {"count" : count, "limit": limit, "skip":skip, "sort": sort, "entries": entries}

    def insert_entry(self, entry):
        result = self.audit.insert_one(entry)

