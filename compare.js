const CompareClass= require('./Compare/CompareClass');
const pathToCC = __dirname + '\\Compare\\attCC.xlsx';
const pathToP = __dirname + '\\Compare\\attPortal.xlsx';
const compare = new CompareClass({file1: pathToP, file2: pathToCC});


async function duplicated () {
    try {
    const portalDevices = await compare.getICCIDs(pathToP, 'Sheet1');
    const duplicated = await compare.findDuplicate(portalDevices);
    console.log(duplicated)
    console.log('DONE')
    } catch (err) {
        console.log(err)
    }

}

async function delta ()  {
    try {
    const controlCenterDevices = await compare.getICCIDs(pathToCC, 'Sheet3');
    const portalDevices = await compare.getICCIDs(pathToP, 'Sheet1');
     const delta = await compare.findDeltaFor(controlCenterDevices, portalDevices)
     const result = await compare.writeToWorksheet({fileName: __dirname+ '\\detla.xlsx', wsName: 'detla', items: delta})
     console.log(result)
     console.log('DONE')
    } catch (err) {
        console.log(err)
    }

}

delta()
console.log('working on it')


