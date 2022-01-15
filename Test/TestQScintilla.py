import sys
import threading
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtCore import Qt
from enum import Enum
from PyQt5.Qsci import *

from Utils.MyLexer import MyLexer
from Utils.logCacher import LocalCache


class CustomMainWindow(QMainWindow):
    def __init__(self):
        super(CustomMainWindow, self).__init__()

        # Window setup
        # --------------

        # 1. Define the geometry of the main window
        self.setGeometry(300, 300, 800, 400)
        self.setWindowTitle("QScintilla Test")

        # 2. Create frame and layout
        self.__frm = QFrame(self)
        self.__frm.setStyleSheet("QWidget { background-color: #ffeaeaea }")
        self.__lyt = QVBoxLayout()
        self.__frm.setLayout(self.__lyt)
        self.setCentralWidget(self.__frm)
        self.__myFont = QFont()
        self.__myFont.setPointSize(14)

        # 3. Place a button
        self.__btn = QPushButton("File")
        self.__btn.setFixedWidth(50)
        self.__btn.setFixedHeight(50)
        self.__btn.clicked.connect(self.__btn_action)
        self.__btn.setFont(self.__myFont)
        self.__lyt.addWidget(self.__btn)

        # 4. init file loader
        self.__logCacher = LocalCache()

        # QScintilla editor setup
        # ------------------------

        # ! Make instance of QsciScintilla class!
        self.__editor = QsciScintilla()
        self.__editor.setLexer(None)
        self.__editor.setUtf8(True)  # Set encoding to UTF-8
        self.__editor.setFont(self.__myFont)  # Will be overridden by lexer!

        vBar = QScrollBar(Qt.Vertical, self)
        vBar.setRange(0, 100)
        vBar.setMaximum(100)
        vBar.setStyleSheet("background : lightgreen;")
        vBar.valueChanged.connect(self.vertPosChanged)
        self.__editor.replaceVerticalScrollBar(vBar)

        self.__editor.setMarginType(0, QsciScintilla.NumberMargin)
        self.__editor.setMarginWidth(0, "000000")
        self.__editor.setMarginsForegroundColor(QColor("#ff888888"))

        # set Lexer for editor
        self.__lexer = MyLexer(self.__editor)
        self.show()

    ''''''

    def vertPosChanged(self, value):
        sender = self.sender()
        ratio = value / self.__editor.lines()
        # if ratio > 0.995:
        #     print('scrolling', str(ratio))
        #     threading.Thread(target=self.test_append_file_into_editor, args=(0.05,),
        #                      daemon=True).start()
        #     ratio = 0.0
        pass

    def __btn_action(self):
        print("reloading...")
        thread = threading.Thread(target=self.test_load_file_into_editor, args=('C:/test/logs_1227.txt', 50),
                                  daemon=True)
        thread.start()

    def test_load_file_into_editor(self, filePath, pages):
        self.__logCacher.reload(filePath, False)
        self.__editor.append(self.__logCacher.get_partial_block(pages))

        # ! append the text style, it is taking long since it would go through all lines
        self.__editor.setLexer(self.__lexer)

        # ! Add editor to layout !
        self.__lyt.addWidget(self.__editor)

    def test_append_file_into_editor(self, pages):
        self.__editor.append(self.__logCacher.get_partial_block(pages))


''''''

''' End Class '''

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    myGUI = CustomMainWindow()

    sys.exit(app.exec_())

''''''
