import os
import re
import subprocess

from PyQt5.QtGui import QColor

from Main.LogEntity import LogEntity


def find_devices():
    commandADB = 'adb devices'
    p = subprocess.Popen(commandADB, shell=True, stdout=subprocess.PIPE)
    # parse the device
    foundedDevices = set()
    out, err = p.communicate()
    for line in out.splitlines():
        line = str(line, encoding='utf-8')
        if line.startswith('List') or line == '' or line == '\n': continue
        deviceId = line.replace('device', '').replace(' ', '').replace('\n', '').replace('\r', '')
        foundedDevices.add(deviceId)
    # all the queried devices
    return foundedDevices


def run_logcat(deviceId, editor):
    # commandADB = 'adb -s ' + deviceId + ' logcat -c && adb -s ' + deviceId + ' logcat'
    subprocess.Popen('adb logcat -c', shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    subprocess.Popen('adb logcat -G 256M', shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    commandADB = 'adb logcat'
    p = subprocess.Popen(commandADB, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1024 * 1024 * 1024)
    cnt = 0
    while p.poll() is None:
        line = p.stdout.readline()
        if line:
            lineStr = str(line, encoding='utf-8').replace('\r\n', '\n')
            editor.append(lineStr)
            cnt += 1
            if cnt % 1000 == 0:
                print(str(cnt))
    if p.returncode == 0:
        print('Subprogram success')
    else:
        print('Subprogram failed')


def clear_cache(deviceId, editor):
    commandADB = 'adb logcat -c'
    if editor:
        editor.clear()
    subprocess.Popen(commandADB, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print('adb logcat cache cleared!')


# parse one Line to logEntity instance
def parse_line_to_log(line):
    logItem = LogEntity()
    pattern_date = re.compile(r"\s+")
    items = pattern_date.split(line)
    itemsLen = len(items)

    if itemsLen < logItem.leastLen:
        logItem.content = line
        logItem.wellAllocated = False
        return logItem

    logItem.timeStamp = items[0] + '_' + items[1]
    logItem.pid = items[2]
    logItem.tid = items[3]
    logItem.level = items[4]
    logItem.tag = items[5][:-1] if items[5][-1] == ':' else items[5][:]
    for item in items[6:]:
        logItem.content += item
    return logItem
