
const request = require('request');

class Devices {
    constructor({baseUrl, token, accountId}) {
        this.token = token;
        this.accountId = accountId;
        this.url = baseUrl + `/devices`
        this.options = {
            url: this.url,
            headers: {
                Accept: 'application/json',
                Authorization: 'Bearer' + " " + this.token,
            }
          };
    }
       async idsForIccids(iccidList) {
                let iccids = {iccids: iccidList}
                let url = this.url + `/iccid?accountId=${this.accountId}`;
                let options = Object.assign({method: 'POST', body: JSON.stringify(iccids) }, this.options);
                return new Promise( (resolve, reject) => {
                    
                    request.post(url, options, 
                        function optionalCallback(err, httpResponse, body) {
                        if (err) {
                            console.error('upload failed:', err);
                            reject(error);
                        }
                        resolve(JSON.parse(body));
                    });
                });
        }

        async readJSONFile() {
            let obj;
            fs.readFile('nlinq', 'utf8', function(err, data) {
                if (err) {
                    console.log(err);
                } else {
                    obj = JSON.parse(data);
                    console.log(obj);
                }
            });
        }
        deleteDevices(ids, customerAccountId) {
            let iccids = {deviceIds: ids, customerAccountId: customerAccountId}
            let url = this.url + `/remove?accountId=${this.accountId}`;
            let options = Object.assign({method: 'put', body: JSON.stringify(iccids) }, this.options);
            console.log(options)
            return new Promise( (resolve, reject) => {
                
                request.put(url, options, 
                    function optionalCallback(err, httpResponse, body) {
                    if (err) {
                        console.error('upload failed:', err);
                        reject(error);
                    }
                    resolve(JSON.parse(body));
                });
            });
        }

        async updateDevice ({deviceId, payload}) {
            let url = this.url + `/${deviceId}?accountId=${this.accountId}`;
            let options = Object.assign({method: 'put', body: JSON.stringify(payload) }, this.options);
           console.log(options.body)
            return new Promise( (resolve, reject) => {
                
                request.put(url, options, 
                    function optionalCallback(err, httpResponse, body) {
                    if (err) {
                        console.error('Assign failed:', err);
                        reject(error);
                    }
                    resolve(JSON.parse(body));
                });
            });
        }

        async assignDevice({payload}) {
            let url = this.url + `/assign?accountId=${this.accountId}`;
            let options = Object.assign({method: 'put', body: JSON.stringify(payload) }, this.options);
           console.log(options.body)
          
            return new Promise( (resolve, reject) => {
                
                request.put(url, options, 
                    function optionalCallback(err, httpResponse, body) {
                    if (err) {
                        console.error('Assign failed:', err);
                        reject(error);
                    }
                    resolve(JSON.parse(body));
                });
            });
        }
}

 module.exports = Devices;
