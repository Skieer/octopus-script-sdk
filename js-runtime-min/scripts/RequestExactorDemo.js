const request = require('request');
try {
  var Extractor = require("../Extractor");
}
catch(err) {
  var Extractor = require("../../Extractor");
}

class RequestExactorDemo extends Extractor {
    /**
     * @param {string[]} mainKeys
     * @returns {Promise<void>}
     * @private
     */
    async _start(loactions) {
        let status = 1;
        for (let location of loactions) {
            try {
                await this.process_item(location)
            } catch(err) {
                super.logError(e);
            }
        }
        status = 2;
        super._onSubTaskFinished(status);
    }

    async process_item(location) {
        let url = `https://free-api.heweather.net/s6/weather/now?location=${location}&key=db86a5196f304e52a4369818c5182e60`
        let res = await this.requestPage(url)
        let j_data_list = JSON.parse(res).HeWeather6
        for(let j_data of j_data_list) {
            let data = {}
            data.cid = j_data.basic.cid;
            data.location = j_data.basic.location;
            data.admin_area = j_data.basic.admin_area;
            data.cnty = j_data.basic.cnty;
            data.cloud = j_data.now.cloud;
            data.cond_code = j_data.now.cond_code;
            data.cond_txt = j_data.now.cond_txt;
            this._onUploadFile(data);
        }
        
    }

    async requestPage(url, proxy=null) {
        let opt = {
            url: url,
            method: 'GET',
            gzip:true,
            timeout:60000,
        }
        if (proxy) {
            opt.proxy = proxy
        }
        super.logInfo("requestPage proxy " + proxy )
        let res = await this.getRequest(opt); //await this.retry(this.getRequest, {params: [opt], default: "{}"});
        super.logInfo("url " + url + " " + res.response.statusCode)
        return res.body;
    }

    // 定义Promise函数
    getRequest(opts) {
        return new Promise ((resolve, reject) => {
            request.get(opts,function(err,response,body){
            //console.log('返回结果：');
            if(!err){
                if(body!=='null'){
                    let results={
                        body : body,
                        response : response
                    };
                    resolve(results);
                }else {
                    reject(err);
                }
            }else {
                reject(err);
            }
            });
        });
    }
}

module.exports = RequestExactorDemo;