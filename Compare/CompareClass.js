const ExcelFile = require('../Common/excel');
const _ = require('underscore');
class CompareICCIDFile {
    constructor({file1, file2}) {
        this.file1 = file1;
        this.file2 = file2;
        this.excel = new ExcelFile();

    }
    async  getICCIDs (fileName, sheetName) {
        const devices = await this.excel.readItemsFromWorksheet(fileName, sheetName);
        return devices;
    } 

    async findDeltaFor(controlCenter, portal) {
        const diff = _.difference(controlCenter, portal);
        return diff;
    }
    async findDuplicate(portal) {
        const object = {};
        const result = [];

        portal.forEach(item => {
          if(!object[item])
              object[item] = 0;
            object[item] += 1;
        })

        for (const prop in object) {
           if(object[prop] >= 2) {
               result.push(prop);
           }
        }

        return result;
    }
    async writeToWorksheet({items, wsName, fileName}) {
        try {
            const result = await this.excel.writeToWorksheet(fileName, wsName, items);
            console.log(result)
            return result
        } catch(err) {
            return err;
        }
    }

}

module.exports = CompareICCIDFile;