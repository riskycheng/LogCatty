# caching the content in dic
import time

from unidecode import unidecode


class LocalCache:
    def __init__(self):
        self.__MAX_LINES_PER_PAGE = 4000  # the max lines inside one same page
        self.__cacheLines_all = []  # simply for speeding up querying
        self.__cachePages_all = []  # simply for speeding up loading
        self.__cacheLines_display = []  # simply for speeding up querying
        self.__cachePages_display = []  # simply for speeding up loading
        self.__numLines_all = 0

    def load_file_to_cache(self, filename):
        print('load_file_to_cache started')
        time_start = time.time()
        self.__cacheLines_all.clear()
        self.__cachePages_all.clear()
        self.__numLines_all = 0
        tempLines = []  # for concat the strings inside same page
        with open(filename, "r", encoding="utf-8", errors="ignore") as file:
            for line in file:
                self.__numLines_all += 1
                line = unidecode(line)
                tempLines.append(line)
                self.__cacheLines_all.append(line)
                if self.__numLines_all % self.__MAX_LINES_PER_PAGE == 0:
                    self.__cachePages_all.append(''.join(each for each in tempLines))
                    tempLines.clear()
        if self.__numLines_all < self.__MAX_LINES_PER_PAGE:
            self.__cachePages_all.append(''.join(each for each in tempLines))
            tempLines.clear()
        print('load_cache_from_file finished: \n\t total pages:%d \n\t total lines:%d' % (
            len(self.__cachePages_all), self.__numLines_all))
        time_finish = time.time()
        print('load_file_to_cache >>> cost %.2fs >>>>:' % (time_finish - time_start))

    def load_content_to_cache(self, text):
        self.__cacheLines_display.clear()
        print('load_content_to_cache started')
        time_start = time.time()
        for line in text:
            self.__cacheLines_display.append(line)
        time_finish = time.time()
        print('load_content_to_cache >>> cost %.2fs >>>>:' % (time_finish - time_start))

    def get_cache_from_display_cache(self, filterStr):
        if filterStr is None or filterStr == '':
            res = ''.join(line for line in self.__cachePages_display)
        else:
            res = ''.join(line if line.find(filterStr) != -1 else '' for line in self.__cacheLines_display)
        return res

    def get_cache_from_all_cache(self, filterStr):
        if filterStr is None:
            res = ''.join(line for line in self.__cachePages_all)
        else:
            res = ''.join(line if line.find(filterStr) != -1 else '' for line in self.__cacheLines_all)
        return res

    def get_cache_allLines(self):
        return self.__cacheLines_all
