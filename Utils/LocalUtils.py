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


def run_logcat(deviceId, editor):
    # commandADB = 'adb -s ' + deviceId + ' logcat -c && adb -s ' + deviceId + ' logcat'
    subprocess.Popen('adb logcat -c')
    commandADB = 'adb logcat'
    p = subprocess.Popen(commandADB, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while p.poll() is None:
        line = p.stdout.readline()
        if line:
            lineStr = str(line, encoding='utf-8')
            editor.append(lineStr)
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
