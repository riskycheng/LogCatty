import os
import re
import subprocess

from PyQt5.Qsci import QsciScintilla
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QColor, QImage
from PyQt5.QtWidgets import QMessageBox

from Utils import logCacher
from Main.LogEntity import LogEntity
from Utils.MyDevice import MyDevice


def call_to_get_result(commandADB):
    p = subprocess.Popen(commandADB, shell=False, stdout=subprocess.PIPE)
    # parse the device
    out, err = p.communicate()
    resultLines = []
    for line in out.splitlines():
        line = str(line, encoding='utf-8')
        resultLines.append(line.replace('\n', ''))
    return resultLines


def find_devices():
    command_queryDevices = '../thirdPartyKit/adb.exe devices'
    resultsQueryDevices = call_to_get_result(command_queryDevices)

    foundedDevices = set()
    for line in resultsQueryDevices:
        if line.startswith('List') or line == '' or line == '\n':
            continue
        if line.endswith('device'):
            deviceId = line.replace('device', '').replace(' ', '').replace('\n', '').replace('\r', '')
            # query its name
            command_queryDeviceName = '../thirdPartyKit/adb.exe -s ' + deviceId + ' shell getprop ro.product.vendor.model'
            deviceNames = call_to_get_result(command_queryDeviceName)
            deviceName = ''
            if len(deviceNames) > 0:
                deviceName = deviceNames[0]

            # query its API-Level
            command_queryAPILevel = '../thirdPartyKit/adb.exe -s ' + deviceId + ' shell getprop ro.build.version.sdk'
            deviceAPIs = call_to_get_result(command_queryAPILevel)
            deviceAPILevel = ''
            if len(deviceAPIs) > 0:
                deviceAPILevel = deviceAPIs[0]

            # query its Factory
            command_queryManufacturer = '../thirdPartyKit/adb.exe -s ' + deviceId + ' shell getprop ro.product.manufacturer'
            deviceManufacturers = call_to_get_result(command_queryManufacturer)
            deviceManufacturer = ''
            if len(deviceManufacturers) > 0:
                deviceManufacturer = deviceManufacturers[0]

            # query its Android version
            command_queryAndroidVersion = '../thirdPartyKit/adb.exe -s ' + deviceId + ' shell getprop ro.build.version.release'
            deviceAndroidVersions = call_to_get_result(command_queryAndroidVersion)
            deviceAndroidVersion = ''
            if len(deviceAndroidVersions) > 0:
                deviceAndroidVersion = deviceAndroidVersions[0]

            # instantiate the device
            thisDevice = MyDevice(deviceID=deviceId, deviceName=deviceName)
            thisDevice.deviceAPILevel = deviceAPILevel
            thisDevice.deviceFactory = deviceManufacturer
            thisDevice.deviceAndroidVersion = deviceAndroidVersion

            foundedDevices.add(thisDevice)
    # all the queried devices
    for device in foundedDevices:
        print('found device => ID:', device.deviceID, ' Name:', device.deviceName, ' Manufacturer:',
              device.deviceFactory, ' API-Level:', device.deviceAPILevel, ' Android:', device.deviceAndroidVersion)
    return foundedDevices


def locateNativeCrashingPoints(symbolLib, addresses):
    commandAddress = '../thirdPartyKit/addr2line_64bit.exe -e ' + symbolLib
    for address in addresses:
        commandAddress += ' ' + address
    p = subprocess.Popen(commandAddress, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    suspiciousLines = []
    while p.poll() is None:
        line = p.stdout.readline()
        if line:
            lineStr = str(line, encoding='utf-8').replace('\r\n', '\n')
            suspiciousLines.append(lineStr)
    if p.returncode != 0:
        print('warning: failed to track crashing point with addr2line')
    return suspiciousLines


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


# move to specific line
def scroll_to_line(editor, lineIndex):
    # scroll to the first line
    start = lineIndex - 10
    editor.setFirstVisibleLine(start if start >= 0 else 0)


def clear_cache(deviceId, editor):
    commandADB = 'adb logcat -c'
    if editor:
        editor.clear()
    subprocess.Popen(commandADB, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print('adb logcat cache cleared!')


# parse one Line to logEntity instance
def parse_adb_logLine_to_log(line):
    logItem = LogEntity()
    pattern_date = re.compile(r"\s+")
    items = pattern_date.split(line)
    itemsLen = len(items)

    if not is_log_line_parseable(line) or itemsLen < logItem.leastLen:
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

    return logItem


# 2022-01-27 15:53:04.337 20237-20237/? W/adbd: timeout expired while flushing socket, closing
def parse_android_studio_logLine_to_log(line):
    logItem = LogEntity()
    pattern = re.compile(r"\s+")
    items = pattern.split(line)
    itemsLen = len(items)

    if not is_log_line_parseable(line):
        logItem.content = line
        logItem.orgText = line
        logItem.wellAllocated = False
        return logItem

    logItem.timeStamp = items[0] + '_' + items[1]
    pid_tid = items[2].split('/')[0].split('-')
    logItem.pid = pid_tid[0]
    logItem.tid = pid_tid[-1]
    logItem.packageName = items[2].split('/')[1]

    logLevel_and_tag = items[3].split('/')
    logItem.level = logLevel_and_tag[0]
    logItem.tag = logLevel_and_tag[1][:-1]

    for item in items[4:]:
        logItem.content += item
    logItem.orgText = line
    if logItem.level == 'E' and logItem.orgText.find('AndroidRuntime: Process') != -1 and logItem.orgText.find(
            'PID') != -1:
        datas = logItem.orgText.split(' ')
        tmpPID = datas[-1].replace(' ', '').replace('\n', '')
        tmpPackage = datas[-3].replace(' ', '').replace(',', '')
        if tmpPID == logItem.pid:
            logItem.packageName = tmpPackage

    return logItem


def check_log_types(file):
    r_android = r"[0-9]{1,4}-[0-1][0-9]-[0-3][0-9]\s+[0-2][0-9]?:[0-6][0-9]?:[0-6][0-9]?.[0-9]{1,3}\s+[0-9]+-[0-9]+/"
    r_adb = r'[0-9|-]{0,4}[0-1][0-9]-[0-3][0-9]\s[0-2][0-9]?:[0-6][0-9]?:[0-6][0-9]?.[0-9]{1,3}\s+[0-9]{1,}\s+[0-9]{1,}\s+[V|v|D|d|I|i|W|w|E|e|F|f|A|a]\s+'
    with open(file, 'r', encoding="utf-8", errors="ignore") as f:
        for line in f:
            match_android = re.match(r_android, line)
            match_adb = re.match(r_adb, line)
            if match_android is None and match_adb is not None:
                return 1  # stands for ADB log
            if match_android is not None and match_adb is None:
                return 2  # stands for android studio log


# can be parsed or not
def is_log_line_parseable(line):
    firstItem = str(line.split(' ')[0]).replace('-', '')
    if firstItem.isalnum() and len(firstItem) >= 4:
        return True
    return False


def parse_line_to_log(line, logType=1):
    if logType == 1:
        return parse_adb_logLine_to_log(line)
    else:
        return parse_android_studio_logLine_to_log(line)


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


def findTargetPositions(logItems):
    suspiciousLines = []
    suspiciousPIDs = set()
    PID_Packages = dict()
    lineIndex = 0
    for logItem in logItems:
        lineIndex += 1
        # check the process IDs
        if logItem.orgText.find('beginning of crash') != -1:
            suspiciousLines.append(lineIndex)

        if logItem.orgText.find('FATAL EXCEPTION') != -1:
            suspiciousPIDs.add(logItem.pid)

        if logItem.orgText.find('backtrace') != -1:
            suspiciousPIDs.add(logItem.pid)
            suspiciousLines.append(lineIndex)

        if logItem.packageName != '' and logItem.pid in suspiciousPIDs:
            print(logItem.toString())
            PID_Packages[logItem.pid] = logItem.packageName

    # results
    print('suspiciousLines: >>>>>>>>>>>>>>>>>>>>')
    for item in suspiciousLines:
        print('\t line[%06d]' % item)

    return suspiciousLines, suspiciousPIDs, PID_Packages


# define function of start recording video
def startRecordVideo():
    print('start calling startRecordVideo')
    command = 'adb shell screenrecord /data/local/tmp/tmp.mp4'
    print('start command execution:%s ...' % command)
    process = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return process


def stopRecordVideo(process, savedPath):
    if process.poll() is None:
        process.terminate()
        process.wait()
    command = 'adb pull /data/local/tmp/tmp.mp4 ' + savedPath
    subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def show_message(message):
    # Create a QMessageBox with an error icon and the error message
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setText(message)
    msg_box.setWindowTitle("Logcatty")
    msg_box.exec_()  # Display the message box
