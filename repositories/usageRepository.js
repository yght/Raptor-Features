const ObjectID = require('mongodb').ObjectID;
const dbUtils = require('../utils/dbUtil');
class UsageRepository {
    constructor({db}) {
        this.usage =  db.collection('usage');
    }
//    async getUsageByDeviceId({accountId, deviceId, skip = 0, limit = 25,from, to, sort = 'id desc'}) {
//         let query = {
//             accountId: new ObjectID(accountId),
//             deviceId: new ObjectID(deviceId),
//             $and: [
//                 { logged: { $gte: new Date(from) }},
//                 { logged: {$lte: new Date(to) }}
//                 ]
//         };
//         const options = {limit, skip, sort: dbUtils.processSortValue(sort)};
//         const count = await this.usage.countDocuments(query);
//         const usage = await this.usage.find(query, options).toArray();
//         return {count: count, result: usage};
//     }

    async getUsageByDeviceId({accountId, deviceId, skip = 0, limit = 100, sort = 'id desc', from, to}) {
        const match = {
           accountId: new ObjectID(accountId),
           deviceId,
           logged: {'$gte':new Date(from), '$lte':new Date(to)}

         };
         const group = {
            _id: {month: {$month: '$logged'}, day:{$dayOfMonth: '$logged'}, year: {$year: '$logged'}},
            logged:{$last: '$logged'},
            mtdData:{$last: '$mtdData'},
         };
         const project = {
            mtdData: 1,
            logged: 1,
            count: 1,
            _id: 0
         }
        const countAggregation = [
            {$match: match},
            {$group: group},
            { $group:{ 
                _id : 1, 
                count: {$sum:1}
            }},
            {$project: {_id: 0}}
        ];
        const aggregate = [
            {$match: match},
            {$group: group},
            {$project: project}
        ];
        const aggregatedCount = await this.usage.aggregate(countAggregation).toArray();
        const count = aggregatedCount.length > 0? aggregatedCount[0].count: 0;
        const usage = await this.usage.aggregate(aggregate).toArray();
        return {count: count, skip, limit, usage: usage};
    }

    async getUsageByPlatform({accountId, platform, skip = 0, limit = 2, sort = 'id desc'}) {
        const query = {accountId: new ObjectID(accountId), platform};
        const options = {limit, skip , sort: dbUtils.processSortValue(sort)};
        const count = await this.usage.countDocuments(query);
        const usage = await this.usage.find(query, options).toArray();
        return {count, result: usage};

    }
}

module.exports = UsageRepository;