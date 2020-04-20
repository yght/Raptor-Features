const dbUtils = require('../utils/dbUtil');
class AuditRepository {
    constructor({db}) {
        this.audit = db.collection('audit');
    }

    async getAuditForIccid({iccid, skip = 0, limit = 10, sort = 'logged desc'}) {
        const query = {iccid: iccid};
        const options = {limit, skip: skip, sort: dbUtils.processSortValue(sort)}
        const count = await this.audit.countDocuments(query);
        const audit = await this.audit.find(query, options).toArray();
        return {result: audit, count};
    }
    async getAuditCountForIccid({iccid, skip, limit, sort = 'logged desc'}) {
        const query = {iccid: iccid};
        const group = {_id: iccid, count: {$sum: 1}};
        const sort = {sort: dbUtils.processSortValue(sort)};
        const result = [{$match: query}, {$group: group}, {$sort: sort}];
       // const options = {limit, skip: skip, sort: dbUtils.processSortValue(sort)}
        
        const auditCount = await this.audit.findOne(result)

        return auditCount;
    }
}

module.exports = AuditRepository;