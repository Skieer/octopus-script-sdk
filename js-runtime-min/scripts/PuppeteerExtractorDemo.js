//通过Api采数据
const puppeteer = require('puppeteer');
try {
    var Extractor = require("../Extractor");
    require("../chrome-extentions/ChromePageExtend");
    require("../chrome-extentions/ChromeElementExtend");
}
catch(err) {
    var Extractor = require("../../Extractor");
    require("../../chrome-extentions/ChromePageExtend");
    require("../../chrome-extentions/ChromeElementExtend");
}
const timeout = function (delay) {
    return new Promise((resolve, reject) => {
        setTimeout(() =>{
        try {
            resolve(1)
        } catch (e) {
            reject(0)
        }
    }, delay);
})
}

class PuppeteerExtractorDemo extends Extractor {
    constructor(context) {
        super(context);
        this.defaultViewport = {
            width: 1920,
            height: 1080
        };
    }

    async _start(urls) {
        let status = 1;
        try {
            await this.startBrowser()
            for(let url of urls) {
                await this.proccess_item(url)
            }
            status = 2;
        } catch (e) {
            super.logError(e);
            status = 1;
        } finally{
            if(this.browser) {
                try {
                    await this.browser.close();
                } catch(e) {
                    super.logError(e);
                }
            }
        }
        super._onSubTaskFinished(status);
    }

    async proccess_item(url) {
        await this.page.goto(url, { waitUntil: 'networkidle0' });
        // Resize the viewport to screenshot elements outside of the viewport
        const bodyHandle = await this.page.$('body');
        const boundingBox = await bodyHandle.boundingBox();
        const newViewport = {
            width: Math.ceil(boundingBox.width),
            height: Math.ceil(boundingBox.height),
        };
        await this.page.setViewport(Object.assign({}, this.defaultViewport, newViewport));
        await timeout(3000)
        await this.page.clickElement("//div[@class='side-drawer-btn']");
        await timeout(3000)
        let el = await this.page.selectOne("//div[@class='body']//ul[@class='comment-list']/..")
        let base64 = await el.screenshot({
            encoding: "base64",
            type: "jpeg",
            omitBackground : true
        });
        let data = {};
        data.image = base64;
        data.title = await this.page.getText("//div[@class='article-content']/h1");
        data.content = await this.page.getText("//div[@class='article-content']/article");
        this._onUploadFile(data);
    }

    async startBrowser(){
        try {
            
            this.browser = await puppeteer.launch({
                headless: true,
                args: [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-infobars',
                    '--window-position=0,0',
                    '--ignore-certifcate-errors',
                    '--ignore-certifcate-errors-spki-list',
                    '--user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3312.0 Safari/537.36"'
                ]
            }); //
            

            this.page = await this.browser.newPage();
            this.page.setViewport(this.defaultViewport);
            await this.page.setDefaultNavigationTimeout(60000);
            await this.page._client.send('Network.clearBrowserCookies');
            // Pass the Webdriver Test.
            await this.page.evaluateOnNewDocument(() => {
                const newProto = navigator.__proto__;
                delete newProto.webdriver;
                navigator.__proto__ = newProto;
            });

            // Pass the Chrome Test.
            await this.page.evaluateOnNewDocument(() => {
                // We can mock this in as much depth as we need for the test.
                window.chrome = {
                runtime: {}
                };
            });

            // Pass the Permissions Test.
            await this.page.evaluateOnNewDocument(() => {
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.__proto__.query = parameters =>
                parameters.name === 'notifications'
                    ? Promise.resolve({state: Notification.permission})
                    : originalQuery(parameters);

                // Inspired by: https://github.com/ikarienator/phantomjs_hide_and_seek/blob/master/5.spoofFunctionBind.js
                const oldCall = Function.prototype.call;
                function call() {
                    return oldCall.apply(this, arguments);
                }
                Function.prototype.call = call;

                const nativeToStringFunctionString = Error.toString().replace(/Error/g, "toString");
                const oldToString = Function.prototype.toString;

                function functionToString() {
                    if (this === window.navigator.permissions.query) {
                    return "function query() { [native code] }";
                    }
                    if (this === functionToString) {
                    return nativeToStringFunctionString;
                    }
                    return oldCall.call(oldToString, this);
                }
                Function.prototype.toString = functionToString;
            });

            // Pass the Plugins Length Test.
            await this.page.evaluateOnNewDocument(() => {
                // Overwrite the `plugins` property to use a custom getter.
                Object.defineProperty(navigator, 'plugins', {
                // This just needs to have `length > 0` for the current test,
                // but we could mock the plugins too if necessary.
                get: () => [1, 2, 3, 4, 5]
                });
            });

            // Pass the Languages Test.
            await this.page.evaluateOnNewDocument(() => {
                // Overwrite the `languages` property to use a custom getter.
                Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
                });
            });

            // Pass the iframe Test
            await this.page.evaluateOnNewDocument(() => {
                Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
                get: function() {
                    return window;
                }
                });
            });

            // Pass toString test, though it breaks console.debug() from working
            await this.page.evaluateOnNewDocument(() => {
                window.console.debug = () => {
                return null;
                };
            });

            return true;
        }catch (e){
            super.logError(e);
            return false;
        }
    }


}

module.exports = PuppeteerExtractorDemo;