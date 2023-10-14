import sys
import threading
import time

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont, QColor, QImage
from PyQt5.QtCore import Qt, QSize
from enum import Enum
from PyQt5.Qsci import *

from Utils import LocalUtils
from Utils.MyLexer import MyLexer
from Utils.logCacher import LocalCache


class MyComboBox(QComboBox):
    def showPopup(self):
        print('start updating the device list')
        self.clear()
        devices = LocalUtils.find_devices()
        for device in devices:
            itemContent = device.deviceFactory + ' ' + device.deviceName + ' Android ' \
                          + device.deviceAndroidVersion + ', API ' + device.deviceAPILevel
            self.addItem(itemContent)
        if len(devices) == 0:
            self.addItem('None')
        print('finish updating the device list')
        super().showPopup()  # Show the dropdown


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
    TOOLKIT_MOVE_PREV = 11
    TOOLKIT_MOVE_NEXT = 12
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
    ToolkitItems.TOOLKIT_MOVE_PREV: "MOVE_PREV",
    ToolkitItems.TOOLKIT_MOVE_NEXT: "MOVE_NEXT",
    ToolkitItems.TOOLKIT_TEST: 'TEST'
}


class MainDesk(QMainWindow):
    def __init__(self):
        super(MainDesk, self).__init__(flags=Qt.WindowFlags())

        self.__logType = 1
        self.__listFilter = None
        self.__regexCheckBox = None
        self.__quickFilter = None
        self.__deviceLabel = None  # this is only the static label name indicating devices
        self.__devices = None
        self.__currentEnabledDevice = None  # this is indicating which device is targeted as connection
        self.__processes = None
        self.__toolkit_lyt = None
        self.__logLevel = None
        self.__logCacher = None
        self.__lexer = None
        self.__myFont = None
        self.__lyt = None
        self.__frm = None
        self.__editor = None

        # cached suspicious lines
        self.__curBreakPointer = -1
        self.__breakPoints = []

        # init the logCacher
        self.__logCacher = LocalCache()

        # start building the UI renderings
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Logcatty Developed by JianCheng v1.0.0.1')
        # accept the file drop
        self.setAcceptDrops(True)

        self.resize(1920, 1080)

        # add toolbar
        # file open
        toolbar = self.addToolBar('File')
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
        # define the toolkit style
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        openToolkit = QAction(QIcon('../res/open_blue.png'), 'open', self)
        openToolkit.setObjectName(ToolkitItemNames[ToolkitItems.TOOLKIT_OPEN])
        toolbar.addAction(openToolkit)

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

        movePrevToolkit = QAction(QIcon('../res/arrow_up.png'), 'Prev', self)
        movePrevToolkit.setObjectName(ToolkitItemNames[ToolkitItems.TOOLKIT_MOVE_PREV])
        toolbar.addAction(movePrevToolkit)

        moveNextToolkit = QAction(QIcon('../res/arrow_down.png'), 'Next', self)
        moveNextToolkit.setObjectName(ToolkitItemNames[ToolkitItems.TOOLKIT_MOVE_NEXT])
        toolbar.addAction(moveNextToolkit)

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

        # - device connection options
        self.__deviceLabel = QLabel()
        self.__deviceLabel.setFont(QFont('Arial', 12))
        self.__toolkit_lyt.addWidget(self.__deviceLabel)
        self.__deviceLabel.setText('Devices')
        self.__deviceLabel.setAlignment(Qt.AlignCenter)
        self.__toolkit_lyt.setStretch(0, 1)

        # - device connection options
        self.__devices = MyComboBox()
        self.__devices.setFont(QFont('Arial', 12))
        self.__devices.setObjectName('devices')
        self.__toolkit_lyt.addWidget(self.__devices)

        self.__toolkit_lyt.setStretch(1, 6)
        # start initial update the device list, it might also be triggered by drop down
        self.queryDevicesAndFillInList()

        # - process options
        self.__processes = QComboBox()
        self.__processes.setFont(QFont('Arial', 12))
        self.__processes.setObjectName('processes')
        self.__processes.addItems(['com.jian.detectx', 'com.system.gallery', 'com.jian.logcatty'])
        self.__toolkit_lyt.addWidget(self.__processes)
        self.__toolkit_lyt.setStretch(2, 10)

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

        # add the marker
        self.__editor.setMarginType(1, QsciScintilla.SymbolMargin)
        self.__editor.setMarginWidth(1, "00000")
        sym_0 = QImage("../res/break_dot.png").scaled(QSize(24, 24))
        self.__editor.markerDefine(sym_0, 0)
        self.__editor.setMarginMarkerMask(1, 0b1111)

        # add slots to post the selected words
        self.__editor.copyAvailable.connect(self.showSelectedWords)

        # add the right click context menu
        self.__editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self.__editor.customContextMenuRequested.connect(self.showCustomContextMenu)

        self.__editor.setAcceptDrops(False)  # set it False to convey it to Parent layer
        self.__lexer = MyLexer(self.__editor, self.__logType)
        # ! Add editor to layout !
        self.__lyt.addWidget(self.__editor, alignment=Qt.Alignment())
        self.__lyt.setStretch(1, 10)  # the second Log content row

    def comboBox_devices_list(self, index):
        # This function will be called when the combo box is clicked
        print(f"Combo Box activated. Selected index: {index}")

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

        # move to prev break point
        elif actionItem.objectName() == ToolkitItemNames[ToolkitItems.TOOLKIT_MOVE_PREV]:
            print(actionItem.text())
            self.move_to_prev_break_point()

        # move to next break point
        elif actionItem.objectName() == ToolkitItemNames[ToolkitItems.TOOLKIT_MOVE_NEXT]:
            print(actionItem.text())
            self.move_to_next_break_point()

        # test action
        elif actionItem.objectName() == ToolkitItemNames[ToolkitItems.TOOLKIT_TEST]:
            print(actionItem.text())
            thread = threading.Thread(target=self.load_file_init, args=('../androidStudioLogs.txt',))
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
        self.__logType = LocalUtils.check_log_types(filePath)
        print(
            'load_file_init begin, load log type: %s' % 'ADB_log' if self.__logType == 1 else 'AS_log')
        self.__lexer.updateLogType(self.__logType)
        # set Lexer for editor
        self.__editor.clear()
        self.__editor.setLexer(None)
        self.__logCacher.load_file_to_cache(filePath, self.__logType)
        self.__editor.append(self.__logCacher.get_cache_from_all_cache(None))

        # ! append the text style, it is taking long since it would go through all lines
        self.__editor.setLexer(self.__lexer)

        time_finish = time.time()
        print('load_file_init >>> cost %.2fs >>>>:' % (time_finish - time_start))

    def start_analyzer(self):
        print('start analyzing..................')
        time_start = time.time()
        content = self.__logCacher.get_cache_allLogItems()
        self.__breakPoints, _, _ = LocalUtils.findTargetPositions(content)
        for lineIndex in self.__breakPoints:
            LocalUtils.add_marker_to_editor(self.__editor, lineIndex)

        time_finish = time.time()
        print('start_analyzer finished >>> cost %.2fs >>>>:' % (time_finish - time_start))

    def move_to_prev_break_point(self):
        length = len(self.__breakPoints)
        if length <= 0:
            return
        self.__curBreakPointer -= 1
        self.__curBreakPointer = self.__curBreakPointer if self.__curBreakPointer >= 0 else 0
        print('move_to_prev_break_point >>> ', str(self.__breakPoints[self.__curBreakPointer]))
        LocalUtils.scroll_to_line(self.__editor, self.__breakPoints[self.__curBreakPointer])

    def move_to_next_break_point(self):
        length = len(self.__breakPoints)
        if length <= 0:
            return
        self.__curBreakPointer += 1
        self.__curBreakPointer = self.__curBreakPointer if self.__curBreakPointer < length else (
                length - 1)
        print('move_to_next_break_point >>> ', str(self.__breakPoints[self.__curBreakPointer]))
        LocalUtils.scroll_to_line(self.__editor, self.__breakPoints[self.__curBreakPointer])

    def dragEnterEvent(self, event):
        if event.mimeData().text().endswith('.txt'):
            event.accept()
        else:
            event.ignore()
        pass

    def dropEvent(self, event):
        path = event.mimeData().text().replace('file:///', '')
        print('load file from:', path)
        thread = threading.Thread(target=self.load_file_init, args=(path,))
        thread.start()
        pass

    # add the selection listener
    # todo search keywords can be acquired here
    def showSelectedWords(self, words):
        print('current selected words:', self.__editor.selectedText())
        pass

    # customize the right click context menu
    # todo trigger and customize more context menu here
    def showCustomContextMenu(self, pos):
        contextMenu = QMenu()
        action1 = QAction('Search', self)
        action1.setObjectName('context_menu_search')
        action2 = QAction('Exclude', self)
        action2.setObjectName('context_menu_exclude')
        # the action of triggering
        action_addr2line = QAction('addr2line', self)
        action_addr2line.setObjectName('context_menu_addr2line')
        action1.triggered.connect(self.contextMenuClickActions)
        action2.triggered.connect(self.contextMenuClickActions)
        action_addr2line.triggered.connect(self.contextMenuClickActions)
        contextMenu.addAction(action1)
        contextMenu.addAction(action2)
        contextMenu.addAction(action_addr2line)
        # get current cursor position
        cursorPos = self.__editor.cursor().pos()
        contextMenu.exec_(cursorPos)

    def contextMenuClickActions(self):
        sender = self.sender()
        objectName = sender.objectName()
        if objectName == 'context_menu_search':
            print('start searching from context : ', self.__editor.selectedText())
        elif objectName == 'context_menu_exclude':
            print('start context_menu_exclude')
        elif objectName == 'context_menu_addr2line':
            print('start context_menu_addr2line')
            selectedAddr = self.__editor.selectedText()
            addresses = [selectedAddr]
            results = LocalUtils.locateNativeCrashingPoints('../Test/nativeCrashDemo/libdetectx-lib.so', addresses)
            print(results)
            QMessageBox.information(self, "Addr2Line", results[0], QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        else:
            print('not supported')

    def queryDevicesAndFillInList(self):
        print('start updating the device list')
        self.__devices.clear()
        devices = LocalUtils.find_devices()
        self.__devices.addItem('None')
        for device in devices:
            itemContent = device.deviceFactory + ' ' + device.deviceName + ' Android ' \
                          + device.deviceAndroidVersion + ', API ' + device.deviceAPILevel
            self.__devices.addItem(itemContent)
        print('finish updating the device list')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainDesk()
    win.show()
    sys.exit(app.exec_())
