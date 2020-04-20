const path = require('path');
const Devices = require('./DeviceBatch/devices.js');
const fs = require('fs');
const baseUrl =`https://raptorwebapiprodwa.azurewebsites.net/api`;
const accountId = '5d6bf1d0c2754f0018ebb4e7';
const token = '';



const devices = new Devices({baseUrl,accountId, token});

// Removal
// (async () => {
//    iccids = await excelAccess.readItemsFromWorksheet(fileName, 'remove');
//    let pageNumber = 0;
//    let pageSize = 100;
//    let customerAccountId = '5d767c02a256a90018437535';
//    let requestedIccids = iccids.slice(pageNumber * pageSize, (pageNumber + 1) * pageSize);
//    while (requestedIccids.length > 0) {
//        console.log(requestedIccids)
//         const deviceListIds = await devices.idsForIccids(requestedIccids);
//         const result = await devices.deleteDevices(deviceListIds.map(d => d.id), customerAccountId);
//         await excelAccess.writeToWorksheet(fileName, 'removed', requestedIccids);
//         await excelAccess.removeFromWorksheet(fileName, 'remove', requestedIccids.length);
//         console.log(result)
//         pageNumber++;
//         requestedIccids = iccids.slice(pageNumber * pageSize, (pageNumber + 1) * pageSize);
//    }
//    // deviceList.forEach(element => { console.log(element.id)});
        
// })();

// Assignment from JSON file for NuvoLinQ
(
   async() => { 
      let nSet = new Set();
      fs.readFile('./devicebatch/test.json', 'utf8', (err, jsonString) => {
         if (err) {
             console.log("File read failed:", err)
             return
         }
         console.log('File data:', jsonString) 
     })
   }
)();
