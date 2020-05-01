const dbUtils = require('../utils/dbUtil');
const ObjectId = require('mongodb').ObjectID;

class AuditRepository {
    constructor({db}) {
        this.audit = db.collection('audit');
    }

    async getAuditForDevice({accountId, deviceId, skip = 0, limit = 100,sort = 'logged desc'}) {
        const query = {
             deviceId: new ObjectId(deviceId),
             accountId: new ObjectId(accountId),  
            };
        const options = {limit, skip: skip, sort: dbUtils.processSortValue(sort)}
        const count = await this.audit.countDocuments(query);
        const audit = await this.audit.find(query, options).toArray();
        return {result: audit, count};
    }
}

module.exports = AuditRepository;