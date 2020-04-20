const ObjectID = require('mongodb').ObjectID;
const dbUtils = {
    processSortValue(sort) {
        const sortFixed = sort.replace('id', '_id');
        const sortSplit = sort.split(' ');
        if (sortSplit.length > 1) {
            return [[...sortSplit]]
        } else 
            return sortFixed;
    },
    convertToObjectId(obj, names) {
        for (let name of names) {
            if (obj[name] && obj[name].length === 24) {
                obj[name] = new ObjectID(obj[name]);
            }
        }
    }

}

module.exports = dbUtils;