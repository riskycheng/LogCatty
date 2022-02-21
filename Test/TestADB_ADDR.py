import os

# import subprocess
# subprocess.Popen('../thirdPartyKit/adb.exe devices', shell=False, close_fds=True)
from Utils import LocalUtils

devices = LocalUtils.find_devices()

for device in devices:
    print(device)

# test addr2lines
# [000000000000ee80 000000000000f084 0000000000010374 00000000000169dc]
addresses = ['000000000000ee80', '000000000000f084', '0000000000010374', '00000000000169dc']
lines = LocalUtils.locateNativeCrashingPoints('../Test/libdetectx-lib.so', addresses)
for line in lines:
    print(line)
