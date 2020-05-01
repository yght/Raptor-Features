
class DeviceFeatures {
constructor({repositories}) {
        this.deviceRepo = repositories.DeviceRepository;
    }

    async updateNewOld({accountId}) {
       return await this.deviceRepo.updateNewOld({accountId});
    }
    async test (accountId) {
        return await this.deviceRepo.updateOldNewCustom({accountId});
    }
    async getDevice({accountId, iccid}) {
        const device = await this.deviceRepo.getDevice({accountId, iccid});
        return device;
    }
    async getDevicesForAccount({accountId}) {
        const result = await this.deviceRepo.getDevicesForAccount({accountId,limit: 10, sort:'mtdData desc'});
        console.log(result.devices.map(d => {return {Data: d.mtdData, iccid: d.iccid}}));
    }

    async getDevicesForL1({accountId, customerL1AccountId}) {
        const result = await this.deviceRepo.getDevicesForL1({accountId, customerL1AccountId});
        console.log(result);
    }

    async getDevicesAggregated() {
        const result = await this.deviceRepo.getAccountDevices({accountId: '5d6bf1d0c2754f0018ebb4e7',skip: 1000, sort: 'created desc'});
        result.devices.map(d => console.log(d))
        return result;
    }
    async getKoreStatus() {
        const result = await this.deviceRepo.getKoreStatus();
        return result;
    }
}

module.exports = DeviceFeatures;