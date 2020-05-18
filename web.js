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
        const accountId = '5d6bf1d0c2754f0018ebb4e7'//'5d6bf1d0c2754f0018ebb4e7' '5d6019afc26e3c0011d372d6'; P:L1:5d716161bd6074001835baa8
        const customerAccountId = '5d767c02a256a90018437535' //'5d62b861c6f0c700118a56d1' 
        const iccid = '89148000005543219463'
       // const {id: deviceId} = await Features.DeviceFeatures.getDevice({accountId, iccid});
       
        // invite

        // Account 


        // PLANS
        // await Features.PlanFeatures.getPlansForCustomer({accountId, customerAccountId})

        // Devices
            //  await Features.DeviceFeatures.getDevicesForL1({accountId, customerL1AccountId:customerAccountId})
             //   await Features.DeviceFeatures.getDevice(iccid)
             // await Features.DeviceFeatures.getDevicesForAccount({accountId})

        // Sync
          
        //   await Features.SyncFeatures.getSyncForIccid({accountId, iccid});
          const syncType = await Features.SyncFeatures.getSyncForType({accountId, type:'error', platform:'jasper'});
           console.log(syncType)
        
        //Audit
        // const result  = await Features.AuditFeatures.getAuditsForDevice({accountId, deviceId, from:'2020-04-17', to:'2020-05-01'}) 
        // console.log(result)
            

         // Usage
            // 
            //  await Features.UsageFeatures.getDeviceUsage({accountId, deviceId,
            //      sort: 'logged desc', limit: 100, 
            //      from :'2019-03-17', 
            //      to:'2026-04-30' 
            //     })
           //  await Features.UsageFeatures.getDataUsageByPlatform({accountId, platform:'kore', sort:'logged desc'})
          //  await Features.UsageFeatures.getDeviceUsage({accountId, deviceId:'5e935e405d0efb058ca583b5'})
        

           
    }catch (err) {
        console.log(err)
    }

}

setup();