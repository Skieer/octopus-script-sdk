const log4js = require("./LogConfig");
const { EventEmitter } = require("events");
const Utils = require('./entities/Utils');
const UseAgentProvider = require('./entities/UseAgentProvider');

module.exports = class Extractor extends EventEmitter {
  /**
   * 初始化 Extractor
   * @param {ExtractorContext} context
   */
  constructor(context) {
    super();
    this._context = context;
    this.utils = new Utils();
  }

  /**
   * 获取 log4js Logger
   * @since 2.0.0
   * @readonly
   * @return {Logger}
   */
  get logger() {
    if (!this._logger) {
      this._logger = log4js.getLogger();
    }
    return this._logger;
  }

  /**
   * 通知采集到了数据
   * @param {JSON} data
   */
  _onUploadFile(data) {
    this.emit("dataExtracted", this._context, data);
  }

  /**
   * 开始采集
   * @private
   */
  start() {
    this.IsStop = false;
    let data = this._context.getParameter("MainKeys");
    this._start(data);
  }

  /**
   * 停止子任务
   */
  stop() {
    this.IsStop = true;
  }

  /**
   * 开始采集
   * 由模版具体实现
   *
   * @param data
   * @returns {Promise<void>}
   */
  async _start(mainKeys) {
    this.logger.error("Override me please");
  }

  /**
   * 采集任务运行完成
   * @param {number} status 1: stop, 2: finished
   * @private
   */
  _onSubTaskFinished(status) {
    this.emit('finished', this._context, status);
  }

  /**
   * 打印 Info 日志
   * @param msg
   */
  logInfo(msg) {
    this.logger.info(msg);
  }

  /**
   * 打印 Info 日志
   * @param exp
   */
  logError(exp) {
    log4js.getLogger('err').error(exp);
  }

  /**
   * 获取代理
   * @returns {Promise<HttpProxy>}
   */
  async getProxy() {
    return await this._context.getProxy();
  }

  /**
   * @returns {boolean}
   */
  isHeadless() {
    return this._context.isHeadless;
  }

  /**
   * 获取随机 UserAgent
   * 保持与原有代码兼容，命名为 getRandUseAgent，这里真实含义应该是 getRandomUserAgent
   *
   * @param {string} type
   * @return {string}
   */
  getRandUseAgent(type) {
    if (!this.useAgentProvider) {
      this.useAgentProvider = new UseAgentProvider();
    }

    let ua;
    switch (type) {
      case 'mobile':
        ua = this.useAgentProvider.getrandomMobileUA();
        break;
      case 'pc':
      default:
        ua = this.useAgentProvider.getrandomPcUA();
        break;
    }
    this.logInfo('getUA' + ua);
  }
};
