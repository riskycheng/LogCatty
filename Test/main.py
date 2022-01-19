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

def test_get_package_name_from_pid(str):
    result = LocalUtils.get_package_name_from_pid(str)
    print(result)

if __name__ == '__main__':
    data = 'this is line data'

    print(data.find('datas'))
