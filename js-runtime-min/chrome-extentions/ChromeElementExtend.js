const Element = require('puppeteer/lib/ElementHandle');

/**
 * 根据Xpath查找一个子元素
 * @param {string} path
 */
Element.prototype.selectOne = async function (path) {
  var elements = await this.$x(path);
  if (elements.length > 0) {
    return elements[0];
  } else {
    return null;
  }
  //return this.$x(path);
};

/**
 * 根据Xpath查找一组子元素
 */
Element.prototype.selectMany = async function (path) {
  var elements = await this.$x(path);
  if (elements.length > 0) {
    return elements;
  } else {
    return null;
  }
}

/**
 * 获取元素文本
 */
Element.prototype.getText = async function () {
  return await this.getAttribute('innerText');
};

/**
 * 获取子元素的文本
 * @param {string} xpath
 */
Element.prototype.getSubText = async function (xpath) {
  var el = await this.selectOne(xpath);
  if (el != null) {
    return await el.getText();
  } else {
    return "";
  }
};

/**
 * 获取元素的innerHtml
 */
Element.prototype.getInnerHtml = async function () {
  return await this.getAttribute('innerHTML');
};

/**
 * 获取子元素的innerHtml
 * @param {string} xpath
 */
Element.prototype.getSubInnerHtml = async function (xpath) {
  var el = await this.selectOne(xpath);
  if (el != null) {
    return await el.getInnerHtml();
  } else {
    return "";
  }
};

/**
 * 获取元素的outerHtml
 */
Element.prototype.getOuterHtml = async function () {
  return await this.getAttribute('outerHTML');
};

/**
 * 获取子元素的outerHtml
 * @param {string} xpath
 */
Element.prototype.getSubOuterHtml = async function (xpath) {
  var el = await this.selectOne(xpath);
  if (el != null) {
    return await el.getOuterHtml();
  } else {
    return "";
  }
};

/**
 * 获取元素的class样式
 */
Element.prototype.getClass = async function () {
  return await this.getAttribute('className');
};

/**
 * 获取子元素的class样式
 * @param {string} xpath
 */
Element.prototype.getSubClass = async function (xpath) {
  var el = await this.selectOne(xpath);
  if (el != null) {
    return await el.getClass();
  } else {
    return "";
  }
};

/**
 * 获取元素的链�
 */
Element.prototype.getLink = async function () {
  return await this.getAttribute('href');
};

/**
 * 获取子元素的链接
 * @param {string} xpath
 */
Element.prototype.getSubLink = async function (xpath) {
  var el = await this.selectOne(xpath);
  if (el != null) {
    return await el.getLink();
  } else {
    return "";
  }
};

Element.prototype.getAttribute = async function (name) {
  var text = await this.getProperty(name);
  if (null != text) {
    return await text.jsonValue();
  } else {
    return "";
  }
};

Element.prototype.getSubAttribute = async function (xpath, name) {
  var el = await this.selectOne(xpath);
  if (el != null) {
    return await el.getAttribute(name);
  } else {
    return "";
  }
};
