import sys
import threading
import time

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtCore import Qt
from enum import Enum
from PyQt5.Qsci import *

from Utils import LocalUtils
from Utils.MyLexer import MyLexer
from Utils.logCacher import LocalCache


class ToolkitItems(Enum):
    TOOLKIT_OPEN = 1
    TOOLKIT_ANALYZE = 2
    TOOLKIT_FILTER = 3
    TOOLKIT_RUN = 4
    TOOLKIT_STOP = 5
    TOOLKIT_CAM = 6
    TOOLKIT_VIDEO = 7
    TOOLKIT_CLEAR = 8
    TOOLKIT_SETTINGS = 9
    TOOLKIT_REFRESH = 10
    TOOLKIT_TEST = -1


ToolkitItemNames = {
    ToolkitItems.TOOLKIT_OPEN: 'OPEN',
    ToolkitItems.TOOLKIT_ANALYZE: 'ANALYZE',
    ToolkitItems.TOOLKIT_FILTER: 'FILTER',
    ToolkitItems.TOOLKIT_RUN: 'RUN',
    ToolkitItems.TOOLKIT_STOP: 'STOP',
    ToolkitItems.TOOLKIT_CAM: 'CAMERA',
    ToolkitItems.TOOLKIT_VIDEO: 'VIDEO',
    ToolkitItems.TOOLKIT_CLEAR: 'CLEAR',
    ToolkitItems.TOOLKIT_SETTINGS: "SETTINGS",
    ToolkitItems.TOOLKIT_REFRESH: "REFRESH",
    ToolkitItems.TOOLKIT_TEST: 'TEST'
}


class MainDesk(QMainWindow):
    def __init__(self):
        super(MainDesk, self).__init__(flags=Qt.WindowFlags())
        self.__listFilter = None
        self.__regexCheckBox = None
        self.__quickFilter = None
        self.__processes = None
        self.__toolkit_lyt = None
        self.__logLevel = None
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
        self.setWindowTitle('Logcatty Developed by JianCheng v1.0.0.1')
        self.resize(1920, 1080)

        # add toolbar
        # file open
        toolbar = self.addToolBar('File')
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
        # define the toolkit style
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        clearToolkit = QAction(QIcon('../res/open_blue.png'), 'open', self)
        clearToolkit.setObjectName(ToolkitItemNames[ToolkitItems.TOOLKIT_OPEN])
        toolbar.addAction(clearToolkit)

        # analyze with native
        debugToolkit = QAction(QIcon('../res/analyze.png'), 'analyze', self)
        debugToolkit.setObjectName(ToolkitItemNames[ToolkitItems.TOOLKIT_ANALYZE])
        toolbar.addAction(debugToolkit)

        # filter the log
        filterToolkit = QAction(QIcon('../res/filter_blue.png'), 'filter', self)
        filterToolkit.setObjectName(ToolkitItemNames[ToolkitItems.TOOLKIT_FILTER])
        toolbar.addAction(filterToolkit)

        # run ro capture logs
        runToolkit = QAction(QIcon('../res/play.png'), 'run', self)
        runToolkit.setObjectName(ToolkitItemNames[ToolkitItems.TOOLKIT_RUN])
        toolbar.addAction(runToolkit)

        # stop capture logs
        stopToolkit = QAction(QIcon('../res/stop.png'), 'stop', self)
        stopToolkit.setObjectName(ToolkitItemNames[ToolkitItems.TOOLKIT_STOP])
        toolbar.addAction(stopToolkit)

        # capture screen
        cameraToolkit = QAction(QIcon('../res/camera.png'), 'camera', self)
        cameraToolkit.setObjectName(ToolkitItemNames[ToolkitItems.TOOLKIT_CAM])
        toolbar.addAction(cameraToolkit)

        # record the video
        videoToolkit = QAction(QIcon('../res/video_green.png'), 'video', self)
        videoToolkit.setObjectName(ToolkitItemNames[ToolkitItems.TOOLKIT_VIDEO])
        toolbar.addAction(videoToolkit)

        # clear the cache
        clearToolkit = QAction(QIcon('../res/delete.png'), 'clear', self)
        clearToolkit.setObjectName(ToolkitItemNames[ToolkitItems.TOOLKIT_CLEAR])
        toolbar.addAction(clearToolkit)

        # additional settings
        settingsToolkit = QAction(QIcon('../res/settings.png'), 'settings', self)
        settingsToolkit.setObjectName(ToolkitItemNames[ToolkitItems.TOOLKIT_SETTINGS])
        toolbar.addAction(settingsToolkit)

        # refresh cache according to current content
        refreshToolkit = QAction(QIcon('../res/refresh.png'), 'refresh', self)
        refreshToolkit.setObjectName(ToolkitItemNames[ToolkitItems.TOOLKIT_REFRESH])
        toolbar.addAction(refreshToolkit)

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
        self.__myFont = QFont("Simsun", 12, weight=QFont.Normal)

        # add the toolkits into first row
        self.__toolkit_lyt = QHBoxLayout()
        # - process options
        self.__processes = QComboBox()
        self.__processes.setFont(QFont('Arial', 12))
        self.__processes.setObjectName('processes')
        self.__processes.addItems(['com.jian.detectx', 'com.system.gallery', 'com.jian.logcatty'])
        self.__toolkit_lyt.addWidget(self.__processes)
        self.__toolkit_lyt.setStretch(0, 3)
        # - log level
        self.__logLevel = QComboBox()
        self.__logLevel.setFont(QFont('Arial', 12))
        self.__logLevel.setObjectName('logLevel')
        self.__logLevel.addItems(['Verbose', 'Debug', 'Info', 'Warn', 'Error', 'Assert'])
        self.__toolkit_lyt.addWidget(self.__logLevel)
        self.__toolkit_lyt.setStretch(1, 1)
        # - quick filter
        self.__quickFilter = QLineEdit()
        self.__quickFilter.setFont(QFont('Arial', 12))
        self.__quickFilter.setObjectName('quickFilter')
        self.__toolkit_lyt.addWidget(self.__quickFilter)
        self.__quickFilter.textChanged.connect(self.onQuickFilterUpdated)
        self.__toolkit_lyt.setStretch(2, 6)
        # - regex checkbox
        self.__regexCheckBox = QCheckBox()
        self.__regexCheckBox.setText('Regex')
        self.__regexCheckBox.setFont(QFont('Arial', 12))
        self.__regexCheckBox.setObjectName('regexCheckBox')
        self.__toolkit_lyt.addWidget(self.__regexCheckBox, alignment=Qt.AlignCenter)
        self.__toolkit_lyt.setStretch(3, 1)
        # - regex checkbox
        self.__listFilter = QComboBox()
        self.__listFilter.setFont(QFont('Arial', 12))
        self.__listFilter.setObjectName('listFilter')
        self.__listFilter.addItems(['Show only selected application', 'No Filters', 'Edit Filter Configuration'])
        self.__toolkit_lyt.addWidget(self.__listFilter)
        self.__toolkit_lyt.setStretch(4, 2)

        self.__lyt.addLayout(self.__toolkit_lyt)
        self.__lyt.setStretch(0, 1)  # the first toolkit row
        # add the QScintilla element
        # QScintilla editor setup
        self.__editor = QsciScintilla()
        self.__editor.setLexer(None)
        self.__editor.setUtf8(True)  # Set encoding to UTF-8
        self.__editor.setFont(self.__myFont)  # to use the style from Lexer
        self.__editor.setReadOnly(True)
        # Margins
        # -----------
        # Margin 0 = Line nr margin
        self.__editor.setMarginType(0, QsciScintilla.NumberMargin)
        self.__editor.setMarginWidth(0, "00000000")
        self.__editor.setMarginsFont(QFont('Arial', 10))
        self.__editor.setMarginsForegroundColor(QColor("#ff888888"))

        # set Lexer for editor
        self.__lexer = MyLexer(self.__editor)
        # ! Add editor to layout !
        self.__lyt.addWidget(self.__editor, alignment=Qt.Alignment())
        self.__lyt.setStretch(1, 10)  # the second Log content row

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
        # debug enabling
        elif actionItem.objectName() == ToolkitItemNames[ToolkitItems.TOOLKIT_ANALYZE]:
            print(actionItem.text())
            thread = threading.Thread(target=self.start_analyzer)
            thread.start()
        # stop action
        elif actionItem.objectName() == ToolkitItemNames[ToolkitItems.TOOLKIT_STOP]:
            print(actionItem.text())
        # run action
        elif actionItem.objectName() == ToolkitItemNames[ToolkitItems.TOOLKIT_RUN]:
            print(actionItem.text())
        # settings action
        elif actionItem.objectName() == ToolkitItemNames[ToolkitItems.TOOLKIT_SETTINGS]:
            print(actionItem.text())
        # refresh action
        elif actionItem.objectName() == ToolkitItemNames[ToolkitItems.TOOLKIT_REFRESH]:
            print(actionItem.text())
        # test action
        elif actionItem.objectName() == ToolkitItemNames[ToolkitItems.TOOLKIT_TEST]:
            print(actionItem.text())
            thread = threading.Thread(target=self.load_file_init, args=('../logs_arrayOutOfIndex.txt',))
            thread.start()
        else:
            print('no supported')

    def onQuickFilterUpdated(self, filterStr):
        print('filtering content with:', filterStr)
        if filterStr == '':
            filterStr = None
        thread = threading.Thread(target=self.reload_all, args=('../logs_0117.txt', -1, filterStr))
        thread.start()
        pass

    def load_file_init(self, filePath):
        time_start = time.time()
        self.__editor.clear()
        self.__logCacher.load_file_to_cache(filePath)
        self.__editor.append(self.__logCacher.get_cache_from_all_cache(None))

        # ! append the text style, it is taking long since it would go through all lines
        self.__editor.setLexer(self.__lexer)

        time_finish = time.time()
        print('load_file_init >>> cost %.2fs >>>>:' % (time_finish - time_start))

    def start_analyzer(self):
        print('start analyzing..................')
        time_start = time.time()
        content = self.__logCacher.get_cache_allLines()
        LocalUtils.findTargetPositions(content)

        time_finish = time.time()
        print('start_analyzer >>> cost %.2fs >>>>:' % (time_finish - time_start))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainDesk()
    win.show()
    sys.exit(app.exec_())
