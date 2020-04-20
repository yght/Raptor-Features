const dbUtils = require('../utils/dbUtil');
const ObjectID = require('mongodb').ObjectID;
const DeviceAPI = require('../DeviceBatch/devices');

const baseUrl =`http://localhost:8000/api`;
const accountId = '5d6bf1d0c2754f0018ebb4e7';
const token = '';
class DeviceRepository {
    constructor({db}) {
        this.device = db.collection('devices');
        this.deviceOLD = db.collection('devices-OLD');
        this.deviceAPI = new DeviceAPI({baseUrl, accountId, token});
    }
    
    replaceId(obj) {
        if (obj === null )
         return ;
        obj.id = obj._id;
        delete obj._id;
    }

    async getDevice (iccid) {
        const query = {iccid: iccid};
        const device = await this.device.findOne(query);
        this.replaceId(device);
        return device;
    }
    async getAccountDevices({accountId, skip = 0, limit = 2, sort = 'id des'}) {
       
        const options = { skip, limit, sort: dbUtils.processSortValue(sort)};
        const query = {accountId: new ObjectID(accountId)};
        const count = await this.device.countDocuments(query);
       // const devices = await this.device.find(query, options).toArray();
        const gr = await this.device.aggregate([{$match: query}, 
            { $group: {
                _id: {
                   day: {$dayOfMonth: '$created'},
                    month: {$month: '$created'},
                    year: {$year: '$created'}
                },
                total: {$sum: 1}
            }
            }, {$sort: {_id: -1}}]).toArray();
        return { count: count, devices: gr};
    }

    async getDevicesForAccount({accountId, skip=0, limit = 100, sort ='id desc'}) {
        const options = { skip, limit, sort: dbUtils.processSortValue(sort)};
        const query = {accountId: new ObjectID(accountId)};
        const count = await this.device.countDocuments(query);
        const devices = await this.device.find(query, options).toArray();
        const result = {devices: devices, count: count}
        return result;
    }

    async getDevicesForL1({accountId, customerL1AccountId, skip=0, limit = 100, sort ='id desc'}) {
        const options = { skip, limit, sort: dbUtils.processSortValue(sort)};
        const query = {"customerL1.accountId": ObjectID(customerL1AccountId)};
        const count = await this.device.countDocuments(query);
        const result = {devices: {}, count: count}
        return result;
    }
    

    async getKoreStatus() {
        const match = {$match: {platform: 'kore'}};
        const group = {$group: {_id: '$kore.status'}}
        const statusQuery = [match, group];
        const result = await this.device.aggregate(statusQuery).toArray();
        return result;
    }
    
    async getAllOld(accountId) {
        const oldQuery = {accountId: new ObjectID(accountId), iccid: '8935201641400798077'}
        const old = await this.deviceOLD.find(oldQuery).toArray();
        return old;
    }
    async updateNewOld({accountId}) {
        const queryNew = {accountId: new ObjectID(accountId)};
       // const options = { skip: 0, limit: 1};
        const devices = await this.device.find(queryNew).toArray();
        const newDevices = devices.filter(device => device.customerL1 === null);
        const newIccids = newDevices.map(d =>  {return {iccid:d.iccid, id: d._id}});
        
        for (var i=0;i<newIccids.length; i++) {
            let newIccid = newIccids[i].iccid;
            let deviceId = newIccids[i].id.toString();
            const old = await this.getAllOld(accountId, newIccid);
            const deviceIds = [deviceId];
            if (old.customerL1 !== null) {
                console.log (old.customerL1.accountId, old.customerL1.planId)
                const payload = {   deviceIds, 
                                    customerAccountId: old.customerL1.accountId,
                                     planId: old.customerL1.planId
                                };

                console.log(payload.customerAccountId, payload.planId, newIccid)
                 const r = await this.deviceAPI.assignDevice({payload})
                console.log(r, i, newIccids.length)

            } else {
                console.log ("NO CUSTOMER ", i, newIccids.length )
            }
           //  console.log(old)
        //     if(old.customerL1 !== null && old.customerL1.accountId !== 'undefined')  {
        //              delete old.customerL1.accountId;
        //              delete old.customerL1.planName;
        //              delete old.customerL1.name;
        //              delete old.customerL1.planId;
        //     }
         
        //     if(old.customerL2 !== null && old.customerL2.accountId !== 'undefined')  {
        //         delete old.customerL2.accountId;
        //         delete old.customerL2.planName;
        //         delete old.customerL2.name;
        //         delete old.customerL2.planId;
        //     }
        //     old.customerL2 = {"field1":"","field2":"","field3":"","field4":"","field5":""}
        //     const payload = {custom: old.custom, customerL1: old.customerL1, customerL2:old.customerL2}
         
        //     console.log(payload, newIccids[i])
        //    const r = await this.deviceAPI.updateDevice({deviceId, payload})
        //     console.log(r)

         }
    }

    async updateOldNewCustom({accountId}) {
       const oldDevices = await this.getAllOld(accountId);
        const query = {accountId: new ObjectID(accountId),
             iccid: '8935201641400798077',"updated": { $lt: new Date("2020-04-13T19:00:07.580+0000") } };
        const allDevices = await this.device.find(query).toArray();
        const newIccids = allDevices.map(d =>  {return {iccid:d.iccid, id: d._id}});
        console.log(newIccids, newIccids.length);
        for (let i = 0; i<newIccids.length; i++) {
            const oldData= oldDevices.find(d => d.iccid === newIccids[i].iccid);
            if (oldData !== null) {
               let payload = {
                    custom: oldData.custom, 
                    customerL1: oldData.customerL1 ,
                     customerL2: oldData.customerL2
                }
                for (let i = 1; i <= 10; i++) {
                    console.log(payload.custom[`field${i}`]);
                    if (payload.custom[`field${i}`] === null ) {
                        payload.custom[`field${i}`] = "";
                    } 
                }
            if (payload.customerL1 !== null ) {
                delete payload.customerL1.accountId;
                delete payload.customerL1.name;
                delete payload.customerL1.planId;
                delete payload.customerL1.planName;
                for (let i = 1; i <= 5; i++) {

                    if (payload.customerL1[`field${i}`] === null ) {
                        payload.customerL1[`field${i}`] = "";
                    } 
                }

            } else {
                delete payload.customerL1
            }
           
            if (payload.customerL2 !== null ) {
                delete payload.customerL2.accountId;
                delete payload.customerL2.name;
                delete payload.customerL2.planId;
                delete payload.customerL2.planName;
                for (let i = 1; i <= 5; i++) {

                    if (payload.customerL2[`field${i}`] === null ) {
                        payload.customerL2[`field${i}`] = "";
                    } 
                }
            } else {
                delete payload.customerL2;
            }
            let deviceId = newIccids[i].id.toString();

            
            await this.deviceAPI.updateDevice({deviceId, payload});
            console.log(i, newIccids[i].iccid);
            }
        }
    }

    // async updateL2({accountId}) {
    //     const oldQuery = {accountId: new ObjectID(accountId), "customerL2.accountId": { $exists: true } }
    //   //  const count = await this.deviceOLD.countDocuments(oldQuery);
    //     const old = await this.deviceOLD.find(oldQuery).toArray();
    //     let iccids = old.map(d => d.iccid);
    //     for (var i=0 ; i<18; i++){
            
    //         const query = {accountId: new ObjectID(accountId), iccid: iccids[i]}
    //         const newDevice = await this.device.findOne(query);
    //         const newDeviceId = newDevice["_id"]
    //         const payload = {deviceIds: [newDeviceId], c}
    //         console.log(newDeviceId);
    //     }
    //     //console.log (count)
    // }
}

module.exports = DeviceRepository;