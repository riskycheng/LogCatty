class MyDevice:
    deviceID = None
    deviceName = None
    deviceFactory = None
    deviceAPILevel = None
    deviceAndroidVersion = None

    def __init__(self, deviceID, deviceName):
        self.deviceID = deviceID
        self.deviceName = deviceName
