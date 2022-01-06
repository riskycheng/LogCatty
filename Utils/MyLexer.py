import re

from PyQt5.Qsci import QsciLexerCustom
from PyQt5.QtGui import QColor, QFont

from Utils import LocalUtils


class MyLexer(QsciLexerCustom):
    def __init__(self, parent):
        super(MyLexer, self).__init__(parent)
        # Default text settings
        # ----------------------
        self.setDefaultColor(QColor("#ff000000"))
        self.setDefaultPaper(QColor("#ffffffff"))
        self.setDefaultFont(QFont("Consolas", 14))

        # Initialize colors per style
        # ----------------------------
        self.setColor(QColor("#ff000000"), 0)  # Style 0: black
        self.setColor(QColor("#ffff0000"), 1)  # Style 1: red
        self.setColor(QColor("#ff0000bf"), 2)  # Style 2: blue
        self.setColor(QColor("#ff007f00"), 3)  # Style 3: green

        # Initialize paper colors per style
        # ----------------------------------
        self.setPaper(QColor("#ffffffff"), 0)  # Style 0: white
        self.setPaper(QColor("#ffffffff"), 1)  # Style 1: white
        self.setPaper(QColor("#ffffffff"), 2)  # Style 2: white
        self.setPaper(QColor("#ffffffff"), 3)  # Style 3: white

        # Initialize fonts per style
        # ---------------------------
        self.setFont(QFont("Consolas", 14, weight=QFont.Bold), 0)  # Style 0: Consolas 14pt
        self.setFont(QFont("Consolas", 14, weight=QFont.Bold), 1)  # Style 1: Consolas 14pt
        self.setFont(QFont("Consolas", 14, weight=QFont.Bold), 2)  # Style 2: Consolas 14pt
        self.setFont(QFont("Consolas", 14, weight=QFont.Bold), 3)  # Style 3: Consolas 14pt

    def language(self):
        return "SimpleLanguage"

    def description(self, style):
        if style == 0:
            return "myStyle_0"
        elif style == 1:
            return "myStyle_1"
        elif style == 2:
            return "myStyle_2"
        elif style == 3:
            return "myStyle_3"
        ###
        return ""

    def styleText(self, start, end):
        # 1. Initialize the styling procedure
        # ------------------------------------
        self.startStyling(start)

        # 2. Slice out a part from the text
        # ----------------------------------
        text = self.parent().text()[start:end]
        lines = text.split('\n')
        for line in lines:
            logItem = LocalUtils.parse_line_to_log(line)
            if logItem.level == 'I':
                # Red style
                self.setStyling(len(line) + 1, 1)
            elif logItem.level == 'D':
                # Black style
                self.setStyling(len(line) + 1, 0)
            elif logItem.level == 'E':
                # Red style
                self.setStyling(len(line) + 1, 2)
            else:
                # Black style
                self.setStyling(len(line) + 1, 0)
