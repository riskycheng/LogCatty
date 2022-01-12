import sys
import threading

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *

from Utils.MyLexer import MyLexer


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
        self.__btn = QPushButton("Qsci")
        self.__btn.setFixedWidth(50)
        self.__btn.setFixedHeight(50)
        self.__btn.clicked.connect(self.__btn_action)
        self.__btn.setFont(self.__myFont)
        self.__lyt.addWidget(self.__btn)

        # QScintilla editor setup
        # ------------------------

        # ! Make instance of QsciScintilla class!
        self.__editor = QsciScintilla()
        self.__editor.setText("Hello\n")
        self.__editor.append("world")
        self.__editor.setLexer(None)
        self.__editor.setUtf8(True)  # Set encoding to UTF-8
        self.__editor.setFont(self.__myFont)  # Will be overridden by lexer!

        self.__editor.setMarginType(0, QsciScintilla.NumberMargin)
        self.__editor.setMarginWidth(0, "000000")
        self.__editor.setMarginsForegroundColor(QColor("#ff888888"))

        # set Lexer for editor
        self.__lexer = MyLexer(self.__editor)

        self.show()
        thread = threading.Thread(target=self.test_load_file_into_editor, args=('c:/test/logsTest.txt',), daemon=True)
        thread.start()
        # self.test_load_file_into_editor('c:/test/logsTest.txt')


    ''''''

    def __btn_action(self):
        print("Hello World!")

    def test_load_file_into_editor(self, filePath):
        file = open(filePath, errors="ignore")
        lineCnt = 0
        totalLines = 0
        data = ''''''

        for line in file:
            totalLines += 1
            if lineCnt < 10000:
                data += line
                lineCnt += 1
            else:
                print('totalLines:', str(totalLines))
                try:
                    self.__editor.append(data)
                    lineCnt = 0
                    data = ''''''
                    pass
                except UnicodeDecodeError as e:
                    print(e, '@', str(lineCnt))
            if totalLines >= 1000000:
                break
        self.__editor.append(data)
        file.close()

        self.__editor.setLexer(self.__lexer)
        # ! Add editor to layout !

        self.__lyt.addWidget(self.__editor)


''''''

''' End Class '''

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    myGUI = CustomMainWindow()

    sys.exit(app.exec_())

''''''
