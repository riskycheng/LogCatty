import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from enum import Enum


class ToolkitItems(Enum):
    TOOLKIT_OPEN = 1
    TOOLKIT_DEBUG = 2
    TOOLKIT_CAM = 3
    TOOLKIT_VIDEO = 4
    TOOLKIT_FILTER = 5
    TOOLKIT_CLEAR = 6


ToolkitItemNames = {
    ToolkitItems.TOOLKIT_OPEN: 'OPEN',
    ToolkitItems.TOOLKIT_DEBUG: 'DEBUG',
    ToolkitItems.TOOLKIT_CAM: 'CAMERA',
    ToolkitItems.TOOLKIT_VIDEO: 'VIDEO',
    ToolkitItems.TOOLKIT_FILTER: 'FILTER',
    ToolkitItems.TOOLKIT_CLEAR: 'CLEAR'
}


def toolkit_click(actionItem):
    # file open
    if actionItem.objectName() == ToolkitItemNames[ToolkitItems.TOOLKIT_OPEN]:
        print(actionItem.text())
    # camera screenshot
    elif actionItem.objectName() == ToolkitItemNames[ToolkitItems.TOOLKIT_CAM]:
        print(actionItem.text())
    # video recording
    elif actionItem.objectName() == ToolkitItemNames[ToolkitItems.TOOLKIT_VIDEO]:
        print(actionItem.text())
    # filter adjustment
    elif actionItem.objectName() == ToolkitItemNames[ToolkitItems.TOOLKIT_FILTER]:
        print(actionItem.text())
    # clear log cache
    elif actionItem.objectName() == ToolkitItemNames[ToolkitItems.TOOLKIT_CLEAR]:
        print(actionItem.text())
    # debug enabling
    elif actionItem.objectName() == ToolkitItemNames[ToolkitItems.TOOLKIT_DEBUG]:
        print(actionItem.text())
    else:
        print('no supported')


class MainDesk(QMainWindow):
    def __init__(self):
        super(MainDesk, self).__init__()
        self.init_UI()

    def init_UI(self):
        self.setWindowTitle('Logcatty')
        self.resize(1280, 720)

        # add toolbar
        # file open
        toolbar = self.addToolBar('File')
        # define the toolkit style
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        clearToolkit = QAction(QIcon('../res/open_blue.png'), 'open', self)
        clearToolkit.setObjectName(ToolkitItemNames[ToolkitItems.TOOLKIT_OPEN])
        toolbar.addAction(clearToolkit)

        # debug with native
        debugToolkit = QAction(QIcon('../res/debug_blue.png'), 'debug', self)
        debugToolkit.setObjectName(ToolkitItemNames[ToolkitItems.TOOLKIT_DEBUG])
        toolbar.addAction(debugToolkit)

        # record the screenshot
        cameraToolkit = QAction(QIcon('../res/camera_blue.png'), 'image', self)
        cameraToolkit.setObjectName(ToolkitItemNames[ToolkitItems.TOOLKIT_CAM])
        toolbar.addAction(cameraToolkit)

        # record the video
        videoToolkit = QAction(QIcon('../res/video_blue.png'), 'video', self)
        videoToolkit.setObjectName(ToolkitItemNames[ToolkitItems.TOOLKIT_VIDEO])
        toolbar.addAction(videoToolkit)

        # filter the log
        filterToolkit = QAction(QIcon('../res/filter_blue.png'), 'filter', self)
        filterToolkit.setObjectName(ToolkitItemNames[ToolkitItems.TOOLKIT_FILTER])
        toolbar.addAction(filterToolkit)

        # clear the cache
        clearToolkit = QAction(QIcon('../res/clear_blue.png'), 'clear', self)
        clearToolkit.setObjectName(ToolkitItemNames[ToolkitItems.TOOLKIT_CLEAR])
        toolbar.addAction(clearToolkit)

        toolbar.actionTriggered.connect(toolkit_click)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainDesk()
    win.show()
    sys.exit(app.exec_())
