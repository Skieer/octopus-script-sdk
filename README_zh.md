# octopus-script-sdk 编写八爪鱼采集脚本的SDK
js-runtime-min 为node js采集脚本的运行环境

云节点上已安装的js库包括, 采集脚本不可以应用超出下面列表，否则脚本会运行不起来
```
{
  "dependencies": {
    "axios": "~0.18.1",
    "cheerio": "^1.0.0-rc.3",
    "commander": "~4.0.1",
    "js2xmlparser": "~4.0.0",
    "jszip": "~3.2.2",
    "log4js": "~4.1.1",
    "lz4js": "~0.2.0",
    "msgpack5": "~4.2.1",
    "proxy-agent": "~3.1.1",
    "puppeteer": "^1.5.0",
    "puppeteer-extra": "^3.1.18",
    "puppeteer-extra-plugin-stealth": "^2.7.8",
    "puppeteer-extra-plugin-user-preferences": "^2.2.12",
    "request": "~2.88.0",
    "sync-request": "~6.1.0",
    "util": "~0.12.1",
    "uuid": "~3.3.3",
    "zlib": "~1.0.5"
  }
}
```
程序入口为：index.js

vs code可添加launch.json配置，具体配置信息为：

```
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "type": "node",
            "request": "launch",
            "name": "Launch Program",
            "program": "${workspaceFolder}\\index.js"
        }
    ]
}
```

拉下代码后，运行 npm install , 初始化好代码环境

采集脚本建议放到scripts目录，现有两个示例脚本
PuppeteerExtractorDemo.js  为使用浏览器来采数据的示例
RequestExactorDemo.js 为使用request请求方式采集数据

调试的时候需要修改MinNode.js两处代码

设置参数，MainKeys是必填参数
```
constructor() {
    this.parameters = new Map();
    //此处改成需要调试脚本的参数
    //Puppeteer demo mainkeys
    //this.parameters.set('MainKeys',["https://www.toutiao.com/a6949819920771220001"]);
    //Request demo mainkeys
    this.parameters.set('MainKeys',["101010100","101020100","101030100"]);
}
```

设置要调试的脚本
```
async doTask(){
    try {
        // 此处改成需要调试的脚本
        //let Extractor = require('./scripts/PuppeteerExtractorDemo');
        let Extractor = require('./scripts/RequestExactorDemo');
        this.extractor = new Extractor(this);
        //script complete
        this.extractor.on("finished", function (node, status) {
            logger.info("finished status" + status);
        });

        //process data
        this.extractor.on("dataExtracted", function (node, data) {
            try {
                fs.appendFileSync('./data/data.json', JSON.stringify(data)+"\r\n");
            } catch(err) {
                logger.error(err)
            }
            
        });

        this.extractor.start();
    } catch(ex) {
        logger.error(ex)
    }
    
}
```
