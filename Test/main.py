import os
import subprocess

from Utils import LocalUtils


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


if __name__ == '__main__':
    filename = 'c:/test/logs_exp.txt'
    with open(filename, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            # print(line)
            for item in line:
                if LocalUtils.is_contain_chinese_or_exASC(item):
                    line = line.replace(item, '?')
            print(line)
