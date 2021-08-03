import logging


class LoggingExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super(LoggingExceptionFormatter, self).formatException(exc_info)
        return repr(result)

    def format(self, record):
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if record.message and record.message[-1:] != "\n":
                record.message = record.message + "\n"
            record.message = record.message + record.exc_text.replace("\\n", "\n")
        if record.stack_info:
            if record.message and record.message[-1:] != "\n":
                record.message = record.message + "\n"
            record.message = record.message + self.formatStack(record.stack_info).replace("\\n", "\n")
        record.message = record.message.replace('"', "'")
        s = self.formatMessage(record)
        return s
