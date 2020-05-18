class SyncFeatures {
    constructor({repositories}) {
        this.syncRepo = repositories.SyncRepository;
    }

    async getSyncForIccid({accountId, iccid}) {
        const result = await this.syncRepo.getSyncForIccid({accountId, iccid, sort:'logged desc', limit:5})
        console.log(result)
    }

    async getSyncForType({accountId, type, platform}) {
        const result = await this.syncRepo.getSyncForType({accountId, type, platform});
       return result;
    }
}

module.exports = SyncFeatures;