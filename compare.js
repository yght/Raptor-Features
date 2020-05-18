const CompareClass= require('./Compare/CompareClass');
const pathToCC = __dirname + '\\Compare\\attCC.xlsx';
const pathToP = __dirname + '\\Compare\\attPortal.xlsx';
const compare = new CompareClass({file1: pathToP, file2: pathToCC});


(async () => {
    try {
    const controlCenterDevices = await compare.getICCIDs(pathToCC, 'Sheet3');
    const portalDevices = await compare.getICCIDs(pathToP, 'Sheet1');
    const delta = await compare.findDeltaFor(controlCenterDevices, portalDevices)
    const result = await compare.writeToWorksheet({fileName: __dirname+ '\\attDelta.xlsx', wsName: 'attDelta', items: delta})
    console.log(result)
    console.log('DONE')
    } catch (err) {
        console.log(err)
    }

})()

console.log('working on it')


