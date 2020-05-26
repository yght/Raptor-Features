from bson import ObjectId
from pymongo import ASCENDING, DESCENDING

def process_sort_value(sort):
    dir = ASCENDING
    if not sort:
        return None
    sort_split = sort.replace('id', '_id').split(' ')
    if len(sort_split) > 1 and sort_split[1].lower() == "desc":
        dir = DESCENDING
    

    return sort_split[0], dir


def rename_object_id(obj):
    if '_id' in obj: obj['id'] = str(obj.pop('_id'))

def delete_object_id(obj):
    if '_id' in obj:
        obj.pop('_id')

def convert_to_string(obj, names):
    if not obj:
        return
    rename_object_id(obj)
    for name in names:
        if name in obj:  obj[name] = str(obj[name])

def convert_to_objectid(obj, names):
    if not obj:
        return
    for name in names:
        if name in obj: obj[name] = ObjectId(obj.pop(name))