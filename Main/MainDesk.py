import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPainter, QColor, QFont, QIcon
from PyQt5.QtCore import Qt


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
        toolbar.addAction(clearToolkit)

        # debug with native
        debugToolkit = QAction(QIcon('../res/debug_blue.png'), 'debug', self)
        toolbar.addAction(debugToolkit)

        # record the screenshot
        cameraToolkit = QAction(QIcon('../res/camera_blue.png'), 'image', self)
        toolbar.addAction(cameraToolkit)

        # record the video
        videoToolkit = QAction(QIcon('../res/video_blue.png'), 'video', self)
        toolbar.addAction(videoToolkit)

        # filter the log
        filterToolkit = QAction(QIcon('../res/filter_blue.png'), 'filter', self)
        toolbar.addAction(filterToolkit)

        # clear the cache
        clearToolkit = QAction(QIcon('../res/clear_blue.png'), 'clear', self)
        toolbar.addAction(clearToolkit)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainDesk()
    win.show()
    sys.exit(app.exec_())
