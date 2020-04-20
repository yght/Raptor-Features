var Excel = require('exceljs');

var wb = new Excel.Workbook();

var path = require('path');
var filePath = path.resolve(__dirname,'globalOrig.xlsx');

async function  readFile() {
   await wb.xlsx.readFile(filePath)
    var portalList = [];
        var controlCenterList = [];
        var portalDevices = wb.getWorksheet("portal");
        var controlCenterDevices = wb.getWorksheet("cc");
    
        portalDevices.getRow(1).getCell(2).value = 32;
    
        for (i = 2; i <= portalDevices.rowCount; i++) {
            let iccid = portalDevices.getRow(i).getCell(1).value;
           portalList.push(iccid);
          
        }
        controlCenterDevices.getRow(1).getCell(2).value = 32;
        for (i = 2; i <= controlCenterDevices.rowCount; i++) {
            let iccid = controlCenterDevices.getRow(i).getCell(1).value;
           controlCenterList.push(iccid);
        }
    
         const common = controlCenterList.filter( x => portalList.includes(x));
         const justInPortal = portalList.filter( x => !controlCenterList.includes(x));
         const justInControlCenter = controlCenterList.filter( x => !portalList.includes(x));
         return {common,   justInPortal,  justInControlCenter};
}

async function createNewFile({common,  justInPortal,  justInControlCenter}) {
    var wb2 = new Excel.Workbook();
    var commonWS =  wb2.addWorksheet('Common');
    var justInPortal =  wb2.addWorksheet('Just Portal');
    var justInCC =  wb2.addWorksheet('Just in CC');
    const toMatrix = (common) => 
    common.reduce((rows, key, index) => (index % 1 == 0 ? rows.push([key]) 
      : rows[rows.length-1].push(key)) && rows, []);

     const commonRows =  toMatrix(common);
    const diffRows = toMatrix(justInPortal);
    const shouldBe = toMatrix(justInControlCenter);
    console.log(shouldBe[500])

    commonWS.addRows(commonRows);
    justInPortal.addRows(diffRows);
    justInCC.addRows(shouldBe);
    await wb2.xlsx.writeFile('resolved.xlsx');
}
async function doTheJob() {
 const {common, wrongAssignment, shouldBeAssigned} = await readFile();
 
 await createNewFile({common, wrongAssignment, shouldBeAssigned});
 console.log('done')
}

doTheJob();

