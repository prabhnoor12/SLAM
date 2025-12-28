from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class FileResultCard(QWidget):
    def __init__(self, filename, path, score, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        icon_label = QLabel("📄")
        icon_label.setStyleSheet("font-size: 24px;")
        info_layout = QVBoxLayout()
        name_label = QLabel(filename)
        name_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 14px;")
        path_label = QLabel(path)
        path_label.setStyleSheet("color: #888888; font-size: 11px;")
        info_layout.addWidget(name_label)
        info_layout.addWidget(path_label)
        score_label = QLabel(f"{int(score)}%")
        color = "#4caf50" if score > 70 else "#ff9800"
        score_label.setStyleSheet(f"""
            color: {color}; 
            background-color: rgba(0,0,0,0.2); 
            padding: 5px; 
            border-radius: 5px; 
            font-weight: bold;
        """)
        layout.addWidget(icon_label)
        layout.addLayout(info_layout, stretch=1)
        layout.addWidget(score_label)
