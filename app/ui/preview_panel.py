from PyQt6.QtWidgets import QFrame, QVBoxLayout, QTextEdit, QLabel

class PreviewPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(300)
        self.setStyleSheet("background-color: #1e1e1e; border-left: 1px solid #333;")
        
        layout = QVBoxLayout(self)
        self.title = QLabel("Document Preview")
        self.title.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet("background-color: transparent; border: none; color: #ccc;")
        
        layout.addWidget(self.title)
        layout.addWidget(self.text_area)

    def update_preview(self, filename, snippet, query):
        self.title.setText(f"Preview: {filename}")
        # Simple HTML highlighting for the query word
        highlighted = snippet.replace(query, f"<span style='background-color: #3d5afe; color: white;'>{query}</span>")
        self.text_area.setHtml(highlighted)
