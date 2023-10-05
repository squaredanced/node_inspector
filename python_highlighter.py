from PySide2.QtCore import QRegExp
from PySide2.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(PythonHighlighter, self).__init__(parent)

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#3579dc"))
        keyword_format.setFontWeight(QFont.Bold)
        self.keywords = [
            "def",
            "return",
            "True",
            "False",
            "self",
            "import",
            "from",
            "as",
        ]

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6a9955"))

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#ce9178"))

        self.highlighting_rules = [
            (QRegExp(r"\b%s\b" % keyword), keyword_format) for keyword in self.keywords
        ]

        self.highlighting_rules.append((QRegExp(r"#.*"), comment_format))
        self.highlighting_rules.append((QRegExp(r"'.*'"), string_format))
        self.highlighting_rules.append((QRegExp(r'".*"'), string_format))

    def highlightBlock(self, text):
        for pattern, _format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, _format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)
