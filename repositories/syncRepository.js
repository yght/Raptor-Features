const ObjectID = require('mongodb').ObjectID;
const dbUtils = require('../utils/dbUtil');

class SyncRepository {
    constructor({db}) {
        this.syncRepo = db.collection('sync')
    }
    async getSyncForIccid({accountId, iccid, skip = 0 , limit = 100, sort ='id desc'}) {
        const query = {accountId: new ObjectID(accountId), iccids: iccid}
        const options = {skip, limit, sort: dbUtils.processSortValue(sort)}
        const count = await this.syncRepo.countDocuments(query);
        const result = await this.syncRepo.find(query, options).toArray();
        const v = result.map(r => {return {type: r.type, logged: r.logged}});
        return {count, v}
    }

    async getSyncForType({accountId, type, skip = 0 , limit = 100, sort ='id desc'}) {
        const query = {accountId: new ObjectID(accountId), type}
        const options = {skip, limit, sort: dbUtils.processSortValue(sort)}
        const count = await this.syncRepo.countDocuments(query);
        const result = await this.syncRepo.find(query, options).toArray();
        return {count, result}
    }
}

module.exports = SyncRepository;