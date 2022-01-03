import os
import subprocess

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
    devices = find_devices()
    print('founded devices:')
    for item in devices:
        print(item)
