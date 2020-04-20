const ObjectID = require('mongodb').ObjectID;
class PlanRepository {
    constructor({db}) {
        this.plan =  db.collection('plans');
    }
    async getPlansForAccount({accountId}) {
        const query = {accountId: ObjectID(accountId)};
        
        const result = await this.plan.find(query).toArray();
        result.count = await this.plan.countDocuments(query);
        return result.count;
    }

    async getPlansForCustomer({accountId, customerAccountId}) {
        const query = {customerAccountId:ObjectID(customerAccountId)}

        const result = await this.plan.find(query).toArray();
        result.count = await this.plan.countDocuments(query);
        return {count: result.count, plans: result};
    }
}

module.exports = PlanRepository;