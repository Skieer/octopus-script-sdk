var MinNode = require('./MinNode.js');
const log4js = require('./LogConfig');
const logger = log4js.getLogger();
const errLogger = log4js.getLogger("err");
var node = new MinNode();

(async() => {
    process.on('uncaughtException', (err) => {
        errLogger.error(err);
    });

    process.on('unhandledRejection', (reason, p) => {
        errLogger.error(reason);
    });

    logger.info("node starting");
    node.start();
 })();
