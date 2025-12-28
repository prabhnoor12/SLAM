
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from app.utils.laucher import open_file


class SearchThread(QThread):
    results_ready = pyqtSignal(list)
    def __init__(self, backend, query):
        super().__init__()
        self.backend = backend
        self.query = query
        self._is_running = True

    def run(self):
        if not self._is_running:
            return
        v = self.backend.engine.encode(self.query)
        self.results_ready.emit(self.backend.db.query(v))

    def stop(self):
        self._is_running = False




class SLAMGui(QMainWindow):
    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        self.setWindowTitle("SLAM AI Search")

        layout = QVBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search content...")
        self.search.textChanged.connect(self.start_timer)

        self.results = QListWidget()
        self.results.itemDoubleClicked.connect(lambda i: open_file(i.data(Qt.ItemDataRole.UserRole)))

        self.clear_btn = QPushButton("Clear Results")
        self.clear_btn.clicked.connect(self.clear_results)

        self.theme_btn = QPushButton("Toggle Theme")
        self.theme_btn.setToolTip("Switch between light and dark themes")
        self.theme_btn.clicked.connect(self.toggle_theme)

        layout.addWidget(self.search)
        layout.addWidget(self.results)
        layout.addWidget(self.clear_btn)
        layout.addWidget(self.theme_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.exec_search)
        self.thread = None

        # Theme support: sync with config
        self.config = getattr(self.backend, 'config', None)
        if self.config:
            self.theme = self.config.settings.get("theme", "light")
        else:
            self.theme = "light"
        self.apply_theme(self.theme)

    def apply_theme(self, theme):
        """Apply the selected theme to the main window."""
        self.theme = theme
        if theme == "dark":
            self.setStyleSheet("""
                QMainWindow { background-color: #232629; color: #f0f0f0; }
                QLabel, QListWidget, QPushButton, QLineEdit { color: #f0f0f0; }
                QListWidget { background: #2c2f33; }
                QPushButton { background: #444; border: 1px solid #666; }
                QLineEdit { background: #2c2f33; border: 1px solid #666; }
            """)
        else:
            self.setStyleSheet("")

    def toggle_theme(self):
        """Toggle between light and dark themes, apply, and sync with config."""
        new_theme = "dark" if self.theme == "light" else "light"
        self.apply_theme(new_theme)
        if self.config:
            self.config.update_config("theme", new_theme)

    def start_timer(self):
        self.timer.stop()
        self.timer.start(350)

    def exec_search(self):
        if self.thread is not None and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()
        self.status.showMessage("Searching...")
        self.thread = SearchThread(self.backend, self.search.text())
        self.thread.results_ready.connect(self.show_results)
        self.thread.start()

    def show_results(self, data):
        self.results.clear()
        for item in data:
            li = QListWidgetItem(f"[{item['score']}%] {item['metadata']['filename']}")
            li.setData(Qt.ItemDataRole.UserRole, item['metadata']['path'])
            self.results.addItem(li)
        self.status.showMessage(f"{len(data)} result(s) found.")

    def clear_results(self):
        self.results.clear()
        self.status.showMessage("Results cleared.")