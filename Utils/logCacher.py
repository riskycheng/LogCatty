# caching the content in dic
from Utils import LocalUtils


class LocalCache:
    def __init__(self):
        self.__MAX_LINES_PER_PAGE = 4000  # will be placed to another page if overflow
        self.__cachePages = []
        self.__numLines = 0
        self.__currentPageIdx = 0

    # reload the file and measure the total length to decide the multi-level paging
    def reload(self, filename):
        print('reload started')
        self.__cachePages.clear()
        self.__numLines = 0
        tempLines = []
        with open(filename, "r", encoding="utf-8", errors="ignore") as file:
            for line in file:
                for item in line:
                    if LocalUtils.is_contain_chinese_or_exASC(item):
                        line = line.replace(item, '?')
                self.__numLines += 1
                tempLines.append(line)
                if self.__numLines % self.__MAX_LINES_PER_PAGE == 0:
                    self.__cachePages.append(''.join(each for each in tempLines))
                    tempLines.clear()
        print('reload finished: \n\t total pages:%d \n\t total lines:%d' % (len(self.__cachePages), self.__numLines))

    def get_partial_block(self, ratio):
        pages = int(len(self.__cachePages) * ratio)
        print('appending finished: \n\t pages from(%d ~ %d) \n\t total lines:%d' % (
            self.__currentPageIdx, self.__currentPageIdx + pages, self.__MAX_LINES_PER_PAGE * pages))
        res = ''.join(each for each in self.__cachePages[self.__currentPageIdx:self.__currentPageIdx + pages])
        self.__currentPageIdx += pages
        return res
