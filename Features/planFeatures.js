class PlanFeatures {
    constructor({repositories}) {
        this.planRepo = repositories.PlanRepository;
    }

    async getPlans({accountId} ){
        const result = await this.planRepo.getPlansForAccount({accountId});
        console.log(result);
    }
    async getPlansForCustomer({accountId, customerAccountId}) {
        const result = await this.planRepo.getPlansForCustomer({accountId, customerAccountId});
        console.log(result)
    }
}

module.exports = PlanFeatures;