const log4js = require('log4js');

log4js.configure({
  replaceConsole: true,
  appenders: {
      stdout: {//控制台输出
          type: 'stdout'
      },
      err: {//错误日志
          type: 'dateFile',
          filename: 'logs/err',
          pattern: 'err-yyyy-MM-dd.log',
          alwaysIncludePattern: true
      },

      oth: {//其他日志
          type: 'dateFile',
          filename: 'logs/oth',
          pattern: 'oth-yyyy-MM-dd.log',
          alwaysIncludePattern: true
      }
  },
  categories: {
      default: { appenders: ['stdout', 'oth'], level: 'debug' },//appenders:采用的appender,取appenders项,level:设置级别
      err: { appenders: ['stdout', 'err'], level: 'error' },
      oth: { appenders: ['stdout', 'oth'], level: 'info' },
  }
});

module.exports = log4js;
