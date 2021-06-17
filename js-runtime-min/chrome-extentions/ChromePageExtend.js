const Page = require('puppeteer/lib/Page');
Page.prototype.selectMany = async function (path) {
  return this.$x(path);
};

Page.prototype.selectOne = async function (path) {
  var elements = await this.$x(path);
  if (elements.length > 0) {
    return elements[0];
  } else {
    return null;
  }
  //return this.$x(path);
};

Page.prototype.waitDocumentComplete = async function (timeout) {
  try {
    await this.waitForNavigation({"waitUntil": 'domcontentloaded', "timeout": timeout});
  } catch (e) {
  }
};

Page.prototype.scrollDown = async function (timeOut) {
  await this.evaluate(_ => {
    window.scrollTo(0, document.body.scrollHeight);
  });
  await this.waitFor(timeOut);
};

Page.prototype.getText = async function (xpath) {
  let el = await this.selectOne(xpath);
  return el.getText();
};

Page.prototype.navigate = async function (url, option) {
  try {
    return await this.goto(url, option);
  } catch (e) {
    return e;
  }
};

Page.prototype.clickElement = async function (xpath) {
  try {
    let el = await this.selectOne(xpath);
    await el.click();
  } catch (e) {

  }
};

Page.prototype.enterText = async function (xpath, text) {
  try {
    let input = await this.selectOne(xpath);
    if (input) {
      await input.type(text);
    }
  } catch (e) {

  }
};
