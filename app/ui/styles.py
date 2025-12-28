STYLE_SHEET = """
QMainWindow {
    background-color: #121212;
}

QLineEdit {
    background-color: #1e1e1e;
    color: #ffffff;
    border: 1px solid #333333;
    border-radius: 10px;
    padding: 12px;
    font-size: 16px;
    selection-background-color: #3d5afe;
}

QLineEdit:focus {
    border: 1px solid #3d5afe;
}

QListWidget {
    background-color: transparent;
    border: none;
    outline: none;
    color: #e0e0e0;
}

QListWidget::item {
    background-color: #1e1e1e;
    margin-bottom: 8px;
    padding: 15px;
    border-radius: 8px;
}

QListWidget::item:selected {
    background-color: #2c2c2c;
    border: 1px solid #3d5afe;
    color: #ffffff;
}

QLabel {
    color: #888888;
    font-size: 12px;
}

QPushButton {
    background-color: #3d5afe;
    color: white;
    border-radius: 5px;
    padding: 8px 15px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #536dfe;
}
"""