import os


def init():
    global _global_dict
    global _log_cache
    _global_dict = {}
    _log_cache = []


def set_value(key, lines):
    _global_dict[key] = lines
    _log_cache.append(lines)

def append_cache(lines):
    _log_cache.append(lines)

def get_value(key):
    try:
        return _global_dict[key]
    except:
        print('fail to read ' + key + '\r\n')


def get_all_cache():
    return _log_cache
