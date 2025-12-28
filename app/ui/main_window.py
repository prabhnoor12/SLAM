
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from app.utils.laucher import open_file
from app.ui.styles import STYLE_SHEET
from app.ui.components import FileResultCard
from app.ui.preview_panel import PreviewPanel


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




    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        self.setStyleSheet(STYLE_SHEET)
        self.setWindowTitle("SLAM AI")
        self.resize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header Area
        header = QHBoxLayout()
        title = QLabel("Smart Search")
        title.setStyleSheet("font-size: 20px; color: white; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(40, 40)
        header.addWidget(self.settings_btn)
        main_layout.addLayout(header)

        # Hero Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Ask anything about your files...")
        self.search_bar.textChanged.connect(self.start_timer)
        main_layout.addWidget(self.search_bar)


        # Results and Preview Area
        content_splitter = QSplitter()
        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.show_preview)
        content_splitter.addWidget(self.results_list)
        self.preview_panel = PreviewPanel()
        content_splitter.addWidget(self.preview_panel)
        content_splitter.setSizes([500, 300])
        main_layout.addWidget(content_splitter)

        # Status Bar
        self.status_bar = QLabel("Ready")
        main_layout.addWidget(self.status_bar)

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
        # Theme is now handled by stylesheet

    # Theme is now handled by stylesheet, so this is a no-op
    def apply_theme(self, theme):
        pass

    def toggle_theme(self):
        # Optionally, implement theme switching logic if you add more themes
        pass

    def start_timer(self):
        self.timer.stop()
        self.timer.start(350)

    def exec_search(self):
        if self.thread is not None and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()
        self.status_bar.setText("Searching...")
        self.thread = SearchThread(self.backend, self.search_bar.text())
        self.thread.results_ready.connect(self.display_results)
        self.thread.start()

    def display_results(self, results):
        self.results = results
        self.results_list.clear()
        for idx, item in enumerate(results):
            meta = item['metadata']
            card = FileResultCard(meta['filename'], meta['path'], item['score'])
            list_item = QListWidgetItem(self.results_list)
            list_item.setSizeHint(card.sizeHint())
            list_item.setData(Qt.ItemDataRole.UserRole, meta['path'])
            list_item.setData(Qt.ItemDataRole.UserRole + 1, idx)
            self.results_list.addItem(list_item)
            self.results_list.setItemWidget(list_item, card)
        self.status_bar.setText(f"{len(results)} result(s) found.")

    def show_preview(self, item):
        idx = item.data(Qt.ItemDataRole.UserRole + 1)
        if idx is not None and 0 <= idx < len(self.results):
            meta = self.results[idx]['metadata']
            snippet = self.results[idx].get('snippet', '')
            query = self.search_bar.text()
            self.preview_panel.update_preview(meta.get('filename', ''), snippet, query)

    def clear_results(self):
        self.results_list.clear()
        self.status_bar.setText("Results cleared.")