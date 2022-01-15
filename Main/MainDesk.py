import sys
import threading
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtCore import Qt
from enum import Enum
from PyQt5.Qsci import *

from Utils import LocalUtils
from Utils.MyLexer import MyLexer
from Utils import logCacher
from Utils.logCacher import LocalCache


class ToolkitItems(Enum):
    TOOLKIT_OPEN = 1
    TOOLKIT_DEBUG = 2
    TOOLKIT_CAM = 3
    TOOLKIT_VIDEO = 4
    TOOLKIT_FILTER = 5
    TOOLKIT_CLEAR = 6
    TOOLKIT_UPDATE_CONTENT = 7
    TOOLKIT_TEST = -1


ToolkitItemNames = {
    ToolkitItems.TOOLKIT_OPEN: 'OPEN',
    ToolkitItems.TOOLKIT_DEBUG: 'DEBUG',
    ToolkitItems.TOOLKIT_CAM: 'CAMERA',
    ToolkitItems.TOOLKIT_VIDEO: 'VIDEO',
    ToolkitItems.TOOLKIT_FILTER: 'FILTER',
    ToolkitItems.TOOLKIT_CLEAR: 'CLEAR',
    ToolkitItems.TOOLKIT_UPDATE_CONTENT: 'UPDATE',
    ToolkitItems.TOOLKIT_TEST: 'TEST'
}


class MainDesk(QMainWindow):
    def __init__(self):
        super(MainDesk, self).__init__(flags=Qt.WindowFlags())
        self.__logCacher = None
        self.__lexer = None
        self.__myFont = None
        self.__lyt = None
        self.__frm = None
        self.__editor = None

        # init the logCacher
        self.__logCacher = LocalCache()

        # start building the UI renderings
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Logcatty')
        self.resize(1920, 1080)

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

        # clear the cache
        updateContentToolkit = QAction(QIcon('../res/update.png'), 'update', self)
        updateContentToolkit.setObjectName(ToolkitItemNames[ToolkitItems.TOOLKIT_UPDATE_CONTENT])
        toolbar.addAction(updateContentToolkit)

        # experimental function
        updateTestToolkit = QAction(QIcon('../res/test_blue.png'), 'test', self)
        updateTestToolkit.setObjectName(ToolkitItemNames[ToolkitItems.TOOLKIT_TEST])
        toolbar.addAction(updateTestToolkit)

        toolbar.actionTriggered.connect(self.toolkit_click)

        # ------------------------ main layout -------------------
        self.__frm = QFrame(self, flags=Qt.WindowFlags())
        self.__frm.setStyleSheet("QWidget { background-color: #ffeaeaea }")
        self.__lyt = QVBoxLayout()
        self.__frm.setLayout(self.__lyt)
        self.setCentralWidget(self.__frm)
        self.__myFont = QFont()
        self.__myFont.setPointSize(14)

        # add the QScintilla element
        # QScintilla editor setup
        self.__editor = QsciScintilla()
        self.__editor.setLexer(None)
        self.__editor.setUtf8(True)  # Set encoding to UTF-8
        self.__editor.setFont(self.__myFont)  # Will be overridden by lexer!

        # Margins
        # -----------
        # Margin 0 = Line nr margin
        self.__editor.setMarginType(0, QsciScintilla.NumberMargin)
        self.__editor.setMarginWidth(0, "000000")
        self.__editor.setMarginsForegroundColor(QColor("#ff888888"))

        # set features
        self.__editor.SendScintilla(QsciScintilla.SC_CACHE_PAGE, 100)
        self.__editor.SendScintilla(QsciScintilla.SCI_SETLAYOUTCACHE, 2)

        # set Lexer for editor
        self.__lexer = MyLexer(self.__editor)

    def reload_all(self, filePath, pages):
        self.__logCacher.reload(filePath)
        self.__editor.append(self.__logCacher.get_partial_block(pages))

        # ! append the text style, it is taking long since it would go through all lines
        self.__editor.setLexer(self.__lexer)

        # ! Add editor to layout !
        self.__lyt.addWidget(self.__editor, alignment=Qt.Alignment())

    def toolkit_click(self, actionItem):
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
            # clear the window cache and device log cache
            LocalUtils.clear_cache(self.__editor, False)
        # debug enabling
        elif actionItem.objectName() == ToolkitItemNames[ToolkitItems.TOOLKIT_DEBUG]:
            print(actionItem.text())
        # updating content in editor
        elif actionItem.objectName() == ToolkitItemNames[ToolkitItems.TOOLKIT_UPDATE_CONTENT]:
            print(actionItem.text())
        elif actionItem.objectName() == ToolkitItemNames[ToolkitItems.TOOLKIT_TEST]:
            print(actionItem.text())
            thread = threading.Thread(target=self.reload_all, args=('c:/test/logs_1227.txt', 100))
            thread.start()
        else:
            print('no supported')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainDesk()
    win.show()
    sys.exit(app.exec_())
