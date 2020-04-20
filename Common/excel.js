var Excel = require('exceljs');



 class ExcelFile {
    constructor() {
        this.wb = new Excel.Workbook();
    }
    async  readItemsFromWorksheet(filename, wsName) {
        
        await this.wb.xlsx.readFile(filename);
        var iccids = [];
        var iccidList = this.wb.getWorksheet(wsName);
        iccidList.getRow(1).getCell(2).value = 32;
        let rowCount = iccidList.rowCount;
        for (var i = 1; i <= rowCount; i++) {
            let iccid = iccidList.getRow(i).getCell(1).value;
            iccids.push(iccid);
        }
        return iccids;  
    };
    async  writeToWorksheet( fileName, wsName, items) {
        var removedWS =  this.wb.getWorksheet(wsName);
        const toMatrix = (common) => 
        common.reduce((rows, key, index) => (index % 1 == 0 ? rows.push([key]) 
          : rows[rows.length-1].push(key)) && rows, []);
    
         const rows =  toMatrix(items);
         removedWS.addRows(rows);
        await this.wb.xlsx.writeFile(fileName);
    }
    async removeFromWorksheet (fileName, wsName, numberOfRows) {
        var removedWS =  this.wb.getWorksheet(wsName);
         removedWS.spliceRows(0, numberOfRows);
         await this.wb.xlsx.writeFile(fileName);
    }
}
module.exports = ExcelFile;

