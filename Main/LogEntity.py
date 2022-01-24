from enum import Enum


class LogLevel(Enum):
    LOG_LEVEL_VERBOSE = 1
    LOG_LEVEL_DEBUG = 2
    LOG_LEVEL_INFO = 3
    LOG_LEVEL_WARN = 4
    LOG_LEVEL_ERROR = 5
    LOG_LEVEL_ASSERT = 6


LogLevelItemNames = {
    LogLevel.LOG_LEVEL_VERBOSE: 'VERBOSE',
    LogLevel.LOG_LEVEL_DEBUG: 'DEBUG',
    LogLevel.LOG_LEVEL_INFO: 'INFO',
    LogLevel.LOG_LEVEL_WARN: 'WARN',
    LogLevel.LOG_LEVEL_ERROR: 'ERROR',
    LogLevel.LOG_LEVEL_ASSERT: 'ASSERT'
}


class LogEntity:
    timeStamp = ''
    tid = ''
    pid = ''
    level = ''
    tag = ''
    wellAllocated = True
    content = ''
    leastLen = 0
    orgText = ''
    packageName = ''

    def __init__(self):
        self.leastLen = 6

    def toString(self):
        res = '\t'
        res += 'wellAllocated:' + ('True' if self.wellAllocated else 'False')
        res += '\n\t'
        res += 'TimeStamp:' + self.timeStamp
        res += '\n\t'
        res += 'PID:' + self.pid
        res += '\n\t'
        res += 'TID:' + self.tid
        res += '\n\t'
        res += 'Package:' + self.packageName
        res += '\n\t'
        res += 'LogLevel:' + self.level
        res += '\n\t'
        res += 'TAG:' + self.tag
        res += '\n\t'
        res += 'Content:' + self.content
        return res
