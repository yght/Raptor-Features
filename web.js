const MongoClient = require("mongodb").MongoClient;
require('dotenv').config();
const config = require('./config');


async function setup() {
    try {
        const client = await MongoClient.connect(config.MONGO_URI, { useNewUrlParser: true });
        var db = client.db(config.MONGO_DB);
        console.log('Connected to DB');

        const repositories = require('./repositories')({db});
        const Features = require('./Features/')({repositories});
       // const DeviceApi = require('./DeviceBatch/devices')()
        const accountId = '5d6019afc26e3c0011d372d6'//'5d6bf1d0c2754f0018ebb4e7' '5d6019afc26e3c0011d372d6'; P:L1:5d716161bd6074001835baa8
        const customerAccountId = '5d767c02a256a90018437535' //'5d62b861c6f0c700118a56d1' 
        const iccid = '89302690201002555442'
        // const iccid = '89302690201000599970';
        // const result = await Features.DeviceFeatures.getDevices();
        // PLANS
        // await Features.PlanFeatures.getPlansForCustomer({accountId, customerAccountId})

        // Devices
            //  await Features.DeviceFeatures.getDevicesForL1({accountId, customerL1AccountId:customerAccountId})
             //   await Features.DeviceFeatures.getDevice(iccid)
             // await Features.DeviceFeatures.getDevicesForAccount({accountId})

        // Sync
          
            await Features.SyncFeatures.getSyncForIccid({accountId, iccid});
         //  await Features.SyncFeatures.getSyncForType({accountId, type:'updated'});
        // Usage
            //  await Features.UsageFeatures.getDeviceUsageByIccid({accountId, iccid,
            //      sort: 'logged desc', limit: 100, 
            //      from :'2019-03-17', 
            //      to:'2026-04-30' 
            //     })
           //  await Features.UsageFeatures.getDataUsageByPlatform({accountId, platform:'kore', sort:'logged desc'})
          //  await Features.UsageFeatures.getDeviceUsage({accountId, deviceId:'5e935e405d0efb058ca583b5'})
        

         // const newIccids =  await Features.DeviceFeatures.updateNewOld({accountId});
         //const t = await Features.DeviceFeatures.test(accountId);
        // console.log(t);
           
           
    }catch (err) {
        console.log(err)
    }

}

setup();