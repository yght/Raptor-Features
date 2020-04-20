class SyncFeatures {
    constructor({repositories}) {
        this.syncRepo = repositories.SyncRepository;
    }

    async getSyncForIccid({accountId, iccid}) {
        const result = await this.syncRepo.getSyncForIccid({accountId, iccid, sort:'logged desc', limit:5})
        console.log(result)
    }

    async getSyncForType({accountId, type}) {
        const result = await this.syncRepo.getSyncForType({accountId, type});
        const devices = result.result.map(m => {return {iccids: m.iccids, error: m.message, type: m.type}})
        console.log(devices);
    }
}

module.exports = SyncFeatures;