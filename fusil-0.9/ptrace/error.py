from sys import exc_info, exc_clear
from traceback import format_exception
from logging import ERROR
from ptrace.logging_tools import getLogFunc, changeLogLevel

PTRACE_ERRORS = Exception

def writeBacktrace(logger, log_level=ERROR, clear=True):
    log_func = getLogFunc(logger, log_level)
    try:
        info = exc_info()
        trace = format_exception(*info)
        if clear:
            exc_clear()
        if trace[0] != "None\n":
            trace = ''.join(trace).rstrip()
            for line in trace.split("\n"):
                log_func(line.rstrip())
            return
    except:
        pass
    log_func("Unable to get backtrace")

def formatError(error):
    return "[%s] %s" % (error.__class__.__name__, error)

def writeError(logger, error, title="ERROR", log_level=ERROR):
    if error.__class__ is SystemExit:
        raise error
    log_func = getLogFunc(logger, log_level)
    log_func("%s: %s" % (title, formatError(error)))
    writeBacktrace(logger, log_level=changeLogLevel(log_level, -1))

class PtraceError(Exception):
    def __init__(self, message, errno=None, pid=None):
        Exception.__init__(self, message)
        self.errno = errno
        self.pid = pid

