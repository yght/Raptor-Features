class UsageFeature {
    constructor({repositories}) {
        this.usageRepo = repositories.UsageRepository;
    }

    // async getDeviceUsage({accountId, deviceId}) {
    //    const result = await this.usageRepo.getUsageByDeviceId({deviceId, accountId});
    //    result.result.forEach(r => console.log(r))
    // } 
    async getDeviceUsage({accountId, deviceId, from, to, sort, limit}) {
        const result = await this.usageRepo.getUsageByDeviceId({deviceId, accountId, from, to, sort, limit});
       console.log(result)
     }
     async getDataUsageByPlatform({accountId, platform, sort}){
         
         const result = await this.usageRepo.getUsageByPlatform({platform, accountId, sort});
         console.log(result);
     }
}

module.exports = UsageFeature;