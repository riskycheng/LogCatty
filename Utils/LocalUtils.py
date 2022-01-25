import os
import re
import subprocess

from PyQt5.Qsci import QsciScintilla
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QColor, QImage
from Utils import logCacher
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


def run_logcat(editor):
    # commandADB = 'adb -s ' + deviceId + ' logcat -c && adb -s ' + deviceId + ' logcat'
    subprocess.Popen('adb logcat -c', shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    subprocess.Popen('adb logcat -G 256M', shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    commandADB = 'adb logcat'
    p = subprocess.Popen(commandADB, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         bufsize=256 * 1024 * 1024)
    while p.poll() is None:
        line = p.stdout.readline()
        if line:
            lineStr = str(line, encoding='utf-8').replace('\r\n', '\n')
    if p.returncode == 0:
        print('Subprogram success')
    else:
        print('Subprogram failed')


# editor related
def add_marker_to_editor(editor, lineIndex):
    editor.markerAdd(lineIndex, 0)


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
        logItem.orgText = line
        logItem.wellAllocated = False
        return logItem

    logItem.timeStamp = items[0] + '_' + items[1]
    logItem.pid = items[2]
    logItem.tid = items[3]
    logItem.level = items[4]
    logItem.tag = items[5][:-1] if items[5][-1] == ':' else items[5][:]
    for item in items[6:]:
        logItem.content += item
    logItem.orgText = line
    if logItem.level == 'E' and logItem.orgText.find('AndroidRuntime: Process') != -1 and logItem.orgText.find(
            'PID') != -1:
        datas = logItem.orgText.split(' ')
        tmpPID = datas[-1].replace(' ', '').replace('\n', '')
        tmpPackage = datas[-3].replace(' ', '').replace(',', '')
        if tmpPID == logItem.pid:
            logItem.packageName = tmpPackage

    if logItem.packageName != '':
        print(logItem.toString())
    return logItem


def is_contain_chinese_or_exASC(check_str):
    """
    :param check_str
    :return: {bool}
    """
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff' or ord(ch) < 0 or ord(ch) > 127:
            return True
    return False


# query the package info according to the given keyword, it could be the PID or partial package name
def get_package_name_from_pid(app_str):
    command = 'adb shell ps |grep ' + app_str
    print('querying package info for given pid info:%s ...' % app_str)
    p = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while p.poll() is None:
        line = p.stdout.readline()
        if line:
            lineStr = str(line, encoding='utf-8').replace('\r\n', '\n')
            if lineStr:
                return lineStr.split(' ')[-1]
    if p.returncode == 0:
        print('Subprogram success')
    else:
        print('Subprogram failed')


def findTargetPositions(content):
    suspiciousLines = []
    suspiciousPIDs = set()
    PID_Packages = dict()
    lineIndex = 0
    for line in content:
        lineIndex += 1
        # check the process IDs
        logItem = parse_line_to_log(line)
        if logItem.orgText.find('beginning of crash') != -1:
            suspiciousLines.append(lineIndex)

        if logItem.orgText.find('FATAL EXCEPTION') != -1:
            suspiciousPIDs.add(logItem.pid)

        if logItem.packageName != '' and logItem.pid in suspiciousPIDs:
            print(logItem.toString())
            PID_Packages[logItem.pid] = logItem.packageName

    # results
    print('suspiciousLines: >>>>>>>>>>>>>>>>>>>>')
    for item in suspiciousLines:
        print('\t line[%06d]' % item)

    print('suspicious PIDs & Packages : >>>>>>>>>>>>>>>>>>>>')
    for item in suspiciousPIDs:
        print('\t PID:%s, Package:%s' % (str(item), PID_Packages[item]))

    return suspiciousLines, suspiciousPIDs, PID_Packages
