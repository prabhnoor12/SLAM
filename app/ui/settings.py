
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QPushButton, 
                             QListWidget, QFileDialog, QHBoxLayout, QLabel)
from PyQt6.QtCore import Qt


class SettingsDialog(QDialog):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.setWindowTitle("SLAM Settings")
        self.setMinimumWidth(450)
        self.setMinimumHeight(300)

        layout = QVBoxLayout()

        # Label
        layout.addWidget(QLabel("<b>Indexed Folders:</b>"))
        layout.addWidget(QLabel("SLAM will monitor these folders for changes and index their content."))

        # Folder List
        self.folder_list = QListWidget()
        self.folder_list.addItems(self.config.settings["watched_folders"])
        layout.addWidget(self.folder_list)

        # Buttons Layout
        btn_layout = QHBoxLayout()

        add_btn = QPushButton("Add Folder")
        add_btn.setToolTip("Select a new folder to index")
        add_btn.clicked.connect(self.add_folder)

        remove_btn = QPushButton("Remove Selected")
        remove_btn.setToolTip("Stop indexing this folder")
        remove_btn.clicked.connect(self.remove_folder)

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setToolTip("Reset all settings to default values")
        reset_btn.clicked.connect(self.reset_defaults)

        theme_btn = QPushButton("Toggle Theme")
        theme_btn.setToolTip("Switch between light and dark themes")
        theme_btn.clicked.connect(self.toggle_theme)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(reset_btn)
        btn_layout.addWidget(theme_btn)
        layout.addLayout(btn_layout)

        # Divider
        line = QLabel("<hr>")
        layout.addWidget(line)

        # Footer Actions
        footer_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        footer_layout.addStretch()
        footer_layout.addWidget(close_btn)
        layout.addLayout(footer_layout)

        self.setLayout(layout)

        # Apply the current theme on startup
        self.apply_theme(self.config.settings.get("theme", "light"))

    def add_folder(self):
        """Opens a native directory picker and updates config only if changed."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Watch")
        if folder and folder not in self.config.settings["watched_folders"]:
            self.config.settings["watched_folders"].append(folder)
            self.config.save_config()
            self.folder_list.addItem(folder)

    def remove_folder(self):
        """Remove selected folder(s) from config and UI."""
        selected = self.folder_list.selectedItems()
        if not selected:
            return
        changed = False
        for item in selected:
            folder = item.text()
            if folder in self.config.settings["watched_folders"]:
                self.config.settings["watched_folders"].remove(folder)
                changed = True
            self.folder_list.takeItem(self.folder_list.row(item))
        if changed:
            self.config.save_config()

    def reset_defaults(self):
        """Reset all settings to default values and update UI."""
        self.config.reset_to_defaults()
        self.folder_list.clear()
        self.folder_list.addItems(self.config.settings["watched_folders"])
        self.apply_theme(self.config.settings.get("theme", "light"))

    def toggle_theme(self):
        """Toggle between light and dark themes and apply immediately."""
        current = self.config.settings.get("theme", "light")
        new_theme = "dark" if current == "light" else "light"
        self.config.update_config("theme", new_theme)
        self.apply_theme(new_theme)

    def apply_theme(self, theme):
        """Apply the selected theme to the dialog."""
        if theme == "dark":
            self.setStyleSheet("""
                QDialog { background-color: #232629; color: #f0f0f0; }
                QLabel, QListWidget, QPushButton { color: #f0f0f0; }
                QListWidget { background: #2c2f33; }
                QPushButton { background: #444; border: 1px solid #666; }
            """)
        else:
            self.setStyleSheet("")

def add_folder(self):
        """Opens a native directory picker and updates config only if changed."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Watch")
        if folder and folder not in self.config.settings["watched_folders"]:
            self.config.settings["watched_folders"].append(folder)
            self.config.save_config()
            self.folder_list.addItem(folder)

def remove_folder(self):
        """Remove selected folder(s) from config and UI."""
        selected = self.folder_list.selectedItems()
        if not selected:
            return
        changed = False
        for item in selected:
            folder = item.text()
            if folder in self.config.settings["watched_folders"]:
                self.config.settings["watched_folders"].remove(folder)
                changed = True
            self.folder_list.takeItem(self.folder_list.row(item))
        if changed:
            self.config.save_config()

def reset_defaults(self):
        """Reset all settings to default values and update UI."""
        self.config.reset_to_defaults()
        self.folder_list.clear()
        self.folder_list.addItems(self.config.settings["watched_folders"])

def toggle_theme(self):
        """Toggle between light and dark themes."""
        current = self.config.settings.get("theme", "light")
        new_theme = "dark" if current == "light" else "light"
        self.config.update_config("theme", new_theme)
        # Optionally, emit a signal or call a method to update the app theme