from pathlib import Path
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QLineEdit, QComboBox, QFileDialog,
    QStackedWidget, QTextEdit, QProgressBar, QTableWidget, QTableWidgetItem,
    QMessageBox, QCheckBox, QHeaderView, QAbstractItemView, QButtonGroup,
)
from app.settings_store import load_settings, save_settings
from core.worker import DownloadWorker
from core.downloader import find_ffmpeg
from storage import database
from ui.theme import DARK_STYLESHEET, LIGHT_STYLESHEET

STATUS_COLORS = {"complete": "#3DD68C", "fail": "#E5484D", "cancel": "#F5A524"}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        database.initialize()
        self.settings = load_settings()
        self.worker = None
        self.last_file = None
        self.setWindowTitle("MediaDownloader")
        self.resize(1120, 760)
        self.setMinimumSize(900, 620)
        self._build_ui()
        self._apply_theme()
        self._refresh_history()
        self._show_page(0)

    # ── Building blocks ──────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(232)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(16, 24, 16, 18)
        side.setSpacing(4)

        brand_row = QHBoxLayout()
        brand_row.setSpacing(12)
        logo = QLabel("↓")
        logo.setObjectName("Logo")
        logo.setFixedSize(40, 40)
        logo.setAlignment(Qt.AlignCenter)
        brand_col = QVBoxLayout()
        brand_col.setSpacing(0)
        brand = QLabel("MediaDownloader")
        brand.setObjectName("Brand")
        sub = QLabel("Windows desktop")
        sub.setObjectName("Muted")
        brand_col.addWidget(brand)
        brand_col.addWidget(sub)
        brand_row.addWidget(logo)
        brand_row.addLayout(brand_col)
        side.addLayout(brand_row)
        side.addSpacing(28)

        self.nav_buttons = []
        for index, label in enumerate(["Home", "Downloads", "History", "Settings"]):
            button = QPushButton(label)
            button.setObjectName("Nav")
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(lambda checked=False, i=index: self._show_page(i))
            side.addWidget(button)
            self.nav_buttons.append(button)
        side.addStretch()

        ok = bool(find_ffmpeg())
        dot, text = ("#3DD68C", "FFmpeg ready") if ok else ("#F5A524", "FFmpeg not found")
        ffmpeg = QLabel(f"<span style='color:{dot}'>●</span>&nbsp; {text}")
        ffmpeg.setObjectName("Muted")
        side.addWidget(ffmpeg)
        root.addWidget(sidebar)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(36, 30, 36, 24)
        self.pages = QStackedWidget()
        self.pages.addWidget(self._build_home())
        self.pages.addWidget(self._build_downloads())
        self.pages.addWidget(self._build_history())
        self.pages.addWidget(self._build_settings())
        content_layout.addWidget(self.pages)
        root.addWidget(content, 1)
        self.setCentralWidget(central)
        self.statusBar().showMessage("Ready")

    def _panel(self, title=None):
        frame = QFrame()
        frame.setObjectName("Panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)
        if title:
            label = QLabel(title)
            label.setObjectName("PanelTitle")
            layout.addWidget(label)
        return frame, layout

    def _heading(self, title, subtitle):
        box = QWidget()
        col = QVBoxLayout(box)
        col.setContentsMargins(0, 0, 0, 6)
        col.setSpacing(2)
        t = QLabel(title)
        t.setObjectName("PageTitle")
        s = QLabel(subtitle)
        s.setObjectName("Muted")
        col.addWidget(t)
        col.addWidget(s)
        return box

    def _field(self, label, widget):
        box = QWidget()
        col = QVBoxLayout(box)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(6)
        name = QLabel(label)
        name.setObjectName("FieldLabel")
        col.addWidget(name)
        if isinstance(widget, QWidget):
            col.addWidget(widget)
        else:
            col.addLayout(widget)
        return box

    def _page(self, title, subtitle):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.addWidget(self._heading(title, subtitle))
        return page, layout

    # ── Pages ────────────────────────────────────────────────────────────────
    def _build_home(self):
        page, layout = self._page("Download media", "Save media you own or have permission to download.")

        panel, form = self._panel()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste a supported media URL here…")
        self.url_input.setClearButtonEnabled(True)
        self.url_input.returnPressed.connect(self._start_download)
        paste = QPushButton("Paste")
        paste.setCursor(Qt.PointingHandCursor)
        paste.clicked.connect(self._paste_url)
        url_row = QHBoxLayout()
        url_row.setSpacing(10)
        url_row.addWidget(self.url_input, 1)
        url_row.addWidget(paste)
        form.addWidget(self._field("Media URL", url_row))

        self.mp3_button = QPushButton("MP3  Audio")
        self.mp3_button.setObjectName("SegLeft")
        self.mp4_button = QPushButton("MP4  Video")
        self.mp4_button.setObjectName("SegRight")
        self.format_group = QButtonGroup(self)
        self.format_group.setExclusive(True)
        seg = QHBoxLayout()
        seg.setSpacing(0)
        for b in (self.mp3_button, self.mp4_button):
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            self.format_group.addButton(b)
            seg.addWidget(b)
        (self.mp3_button if self.settings["default_format"] == "mp3" else self.mp4_button).setChecked(True)

        self.output_input = QLineEdit(self.settings["download_dir"])
        browse = QPushButton("Browse")
        browse.clicked.connect(self._browse_output)
        out_row = QHBoxLayout()
        out_row.setSpacing(10)
        out_row.addWidget(self.output_input, 1)
        out_row.addWidget(browse)

        options = QHBoxLayout()
        options.setSpacing(24)
        options.addWidget(self._field("Format", seg))
        options.addWidget(self._field("Save to", out_row), 1)
        form.addLayout(options)

        self.start_button = QPushButton("Start download")
        self.start_button.setObjectName("Primary")
        self.start_button.setCursor(Qt.PointingHandCursor)
        self.start_button.clicked.connect(self._start_download)
        form.addWidget(self.start_button)
        layout.addWidget(panel)

        progress_panel, pl = self._panel("Current download")
        head = pl.itemAt(0).widget()
        pl.removeWidget(head)
        top = QHBoxLayout()
        top.addWidget(head)
        top.addStretch()
        self.progress_text = QLabel("Waiting for a URL")
        self.progress_text.setObjectName("Chip")
        top.addWidget(self.progress_text)
        pl.insertLayout(0, top)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        pl.addWidget(self.progress_bar)

        bottom = QHBoxLayout()
        self.progress_details = QLabel("Speed: —    ETA: —")
        self.progress_details.setObjectName("Muted")
        self.percent_label = QLabel("0%")
        self.percent_label.setObjectName("Percent")
        self.cancel_button = QPushButton("Cancel download")
        self.cancel_button.setObjectName("Danger")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self._cancel_download)
        bottom.addWidget(self.percent_label)
        bottom.addSpacing(14)
        bottom.addWidget(self.progress_details)
        bottom.addStretch()
        bottom.addWidget(self.cancel_button)
        pl.addLayout(bottom)
        layout.addWidget(progress_panel)

        log_panel, log_layout = self._panel("Activity")
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMinimumHeight(120)
        self.log_view.setPlaceholderText("Download activity will appear here.")
        log_layout.addWidget(self.log_view)
        layout.addWidget(log_panel, 1)
        return page

    def _build_downloads(self):
        page, layout = self._page("Downloads", "Your current activity appears on the Home page.")
        panel, inner = self._panel("Latest download")
        self.downloads_status = QLabel("No active download.")
        self.downloads_status.setObjectName("Muted")
        self.downloads_status.setWordWrap(True)
        inner.addWidget(self.downloads_status)
        row = QHBoxLayout()
        row.setSpacing(10)
        self.open_file_button = QPushButton("Open file")
        self.open_file_button.setEnabled(False)
        self.open_file_button.clicked.connect(self._open_file)
        open_folder = QPushButton("Open download folder")
        open_folder.clicked.connect(self._open_folder)
        row.addWidget(open_folder)
        row.addWidget(self.open_file_button)
        row.addStretch()
        inner.addLayout(row)
        layout.addWidget(panel)
        layout.addStretch()
        return page

    def _build_history(self):
        page, layout = self._page("Download history", "Completed and failed download attempts stored on this PC.")
        panel, inner = self._panel()
        self.history_empty = QLabel("No downloads yet. Finished downloads will show up here.")
        self.history_empty.setObjectName("Muted")
        self.history_empty.setAlignment(Qt.AlignCenter)
        inner.addWidget(self.history_empty)

        self.history_table = QTableWidget(0, 5)
        self.history_table.setHorizontalHeaderLabels(["Title", "Format", "Status", "Saved file", "Date"])
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setHighlightSections(False)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.verticalHeader().setDefaultSectionSize(42)
        self.history_table.setShowGrid(False)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.history_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        inner.addWidget(self.history_table, 1)

        buttons = QHBoxLayout()
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self._refresh_history)
        clear = QPushButton("Clear history")
        clear.setObjectName("Danger")
        clear.clicked.connect(self._clear_history)
        buttons.addWidget(refresh)
        buttons.addStretch()
        buttons.addWidget(clear)
        inner.addLayout(buttons)
        layout.addWidget(panel, 1)
        return page

    def _build_settings(self):
        page, layout = self._page("Settings", "Local preferences only. No API keys or account configuration.")
        panel, form = self._panel()

        self.settings_format = QComboBox()
        self.settings_format.addItems(["MP3", "MP4"])
        self.settings_format.setCurrentIndex(0 if self.settings["default_format"] == "mp3" else 1)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setCurrentText(self.settings["theme"].capitalize())
        self.audio_quality = QComboBox()
        self.audio_quality.addItems(["128", "192", "256", "320"])
        self.audio_quality.setCurrentText(str(self.settings["audio_quality"]))
        self.video_quality = QComboBox()
        self.video_quality.addItems(["360", "480", "720", "1080", "1440", "2160"])
        self.video_quality.setCurrentText(str(self.settings["video_quality"]))

        grid = QGridLayout()
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(16)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.addWidget(self._field("Default format", self.settings_format), 0, 0)
        grid.addWidget(self._field("Theme", self.theme_combo), 0, 1)
        grid.addWidget(self._field("MP3 quality (kbps)", self.audio_quality), 1, 0)
        grid.addWidget(self._field("Maximum MP4 video height (p)", self.video_quality), 1, 1)
        form.addLayout(grid)

        self.embed_thumbnail = QCheckBox("Embed available thumbnail in MP3")
        self.embed_thumbnail.setChecked(bool(self.settings["embed_thumbnail"]))
        self.fetch_lyrics = QCheckBox("Try to fetch synced lyrics for MP3")
        self.fetch_lyrics.setChecked(bool(self.settings["fetch_lyrics"]))
        form.addWidget(self.embed_thumbnail)
        form.addWidget(self.fetch_lyrics)

        footer = QHBoxLayout()
        ffmpeg_label = QLabel(
            "FFmpeg detected." if find_ffmpeg()
            else "FFmpeg not detected — required for MP3 conversion and MP4 merging."
        )
        ffmpeg_label.setObjectName("Muted")
        save = QPushButton("Save settings")
        save.setObjectName("Primary")
        save.clicked.connect(self._save_settings)
        footer.addWidget(ffmpeg_label)
        footer.addStretch()
        footer.addWidget(save)
        form.addLayout(footer)
        layout.addWidget(panel)
        layout.addStretch()
        return page

    # ── Theme / navigation ───────────────────────────────────────────────────
    def _apply_theme(self):
        self.setStyleSheet(DARK_STYLESHEET if self.settings.get("theme") == "dark" else LIGHT_STYLESHEET)

    def _show_page(self, index):
        self.pages.setCurrentIndex(index)
        for i, button in enumerate(self.nav_buttons):
            button.setProperty("active", i == index)
            button.style().unpolish(button)
            button.style().polish(button)
        if index == 2:
            self._refresh_history()

    # ── Actions ──────────────────────────────────────────────────────────────
    def _selected_format(self):
        return "mp3" if self.mp3_button.isChecked() else "mp4"

    def _paste_url(self):
        text = QApplication.clipboard().text().strip()
        if text:
            self.url_input.setText(text)

    def _browse_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose download folder", self.output_input.text())
        if folder:
            self.output_input.setText(folder)

    def _start_download(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.information(self, "Download running", "Wait for the current download to finish.")
            return
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Missing URL", "Paste a media URL first.")
            return
        output = self.output_input.text().strip()
        if not output:
            QMessageBox.warning(self, "Missing folder", "Choose a download folder.")
            return
        media_format = self._selected_format()
        Path(output).mkdir(parents=True, exist_ok=True)
        self.settings["download_dir"] = output
        self.settings["default_format"] = media_format
        save_settings(self.settings)
        self.log_view.append(f"URL: {url}\nFormat: {media_format.upper()}\nFolder: {output}")
        self.progress_bar.setValue(0)
        self.percent_label.setText("0%")
        self.progress_text.setText("Starting…")
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.open_file_button.setEnabled(False)
        self.downloads_status.setText(f"Downloading {media_format.upper()}…")
        self.worker = DownloadWorker(url, media_format, output, self.settings.copy())
        self.worker.progress.connect(self._on_progress)
        self.worker.log.connect(self._append_log)
        self.worker.completed.connect(self._on_completed)
        self.worker.failed.connect(self._on_failed)
        self.worker.cancelled.connect(self._on_cancelled)
        self.worker.finished.connect(self._worker_finished)
        self.worker.start()

    def _on_progress(self, percent, speed, eta, filename):
        self.progress_bar.setValue(percent)
        self.percent_label.setText(f"{percent}%")
        name = Path(filename).name if filename else f"{percent}%"
        self.progress_text.setText(self._elide(name, 48))
        self.progress_details.setText(f"Speed: {speed or '—'}    ETA: {eta or '—'}")

    @staticmethod
    def _elide(text, limit):
        return text if len(text) <= limit else text[: limit - 1] + "…"

    def _append_log(self, message):
        self.log_view.append(message)
        self.statusBar().showMessage(message.splitlines()[0] if message else "", 5000)

    def _on_completed(self, title, filepath):
        self.last_file = filepath
        self.progress_bar.setValue(100)
        self.percent_label.setText("100%")
        self.progress_text.setText("Completed")
        self._append_log(f"Completed: {title}\nSaved: {filepath}")
        self.downloads_status.setText(f"Completed: {title}\n{filepath}")
        self.open_file_button.setEnabled(True)
        self._refresh_history()
        QMessageBox.information(self, "Download complete", f"{title}\n\nSaved to:\n{filepath}")

    def _on_failed(self, error):
        self.progress_text.setText("Failed")
        self._append_log(f"ERROR: {error}")
        self.downloads_status.setText("The download failed.")
        QMessageBox.critical(self, "Download failed", error)

    def _on_cancelled(self):
        self.progress_text.setText("Cancelled")
        self._append_log("Download cancelled.")
        self.downloads_status.setText("Download cancelled.")
        self._refresh_history()

    def _worker_finished(self):
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.worker = None

    def _cancel_download(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.cancel_button.setEnabled(False)
            self._append_log("Cancellation requested…")

    def _open_folder(self):
        folder = self.output_input.text().strip() or self.settings["download_dir"]
        Path(folder).mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def _open_file(self):
        if self.last_file and Path(self.last_file).exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.last_file))
        else:
            QMessageBox.information(self, "File not found", "The saved file is no longer at that location.")

    def _refresh_history(self):
        if not hasattr(self, "history_table"):
            return
        rows = database.get_downloads()
        self.history_empty.setVisible(not rows)
        self.history_table.setVisible(bool(rows))
        self.history_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            values = [row["title"], row["media_format"].upper(), row["status"],
                      row["output_path"], row["created_at"]]
            for c, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if c == 2:
                    for key, color in STATUS_COLORS.items():
                        if key in str(value).lower():
                            item.setForeground(QColor(color))
                            break
                self.history_table.setItem(r, c, item)

    def _clear_history(self):
        answer = QMessageBox.question(self, "Clear history", "Delete all download history records?")
        if answer == QMessageBox.Yes:
            database.clear_history()
            self._refresh_history()

    def _save_settings(self):
        self.settings.update({
            "default_format": "mp3" if self.settings_format.currentIndex() == 0 else "mp4",
            "audio_quality": self.audio_quality.currentText(),
            "video_quality": self.video_quality.currentText(),
            "embed_thumbnail": self.embed_thumbnail.isChecked(),
            "fetch_lyrics": self.fetch_lyrics.isChecked(),
            "theme": self.theme_combo.currentText().lower(),
        })
        save_settings(self.settings)
        self._apply_theme()
        self._append_log("Settings saved.")
        QMessageBox.information(self, "Settings", "Your settings have been saved.")
# from pathlib import Path
# from PySide6.QtCore import Qt, QUrl
# from PySide6.QtGui import QDesktopServices
# from PySide6.QtWidgets import (
#     QMainWindow, QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
#     QLineEdit, QComboBox, QFileDialog, QStackedWidget, QTextEdit, QProgressBar,
#     QTableWidget, QTableWidgetItem, QMessageBox, QCheckBox, QSpinBox, QHeaderView,
#     QAbstractItemView
# )
# from app.settings_store import load_settings, save_settings
# from core.worker import DownloadWorker
# from core.downloader import find_ffmpeg
# from storage import database
# from ui.theme import DARK_STYLESHEET, LIGHT_STYLESHEET

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         database.initialize()
#         self.settings = load_settings()
#         self.worker = None
#         self.setWindowTitle("MediaDownloader")
#         self.resize(1120, 760)
#         self.setMinimumSize(900, 620)
#         self._build_ui()
#         self._apply_theme()
#         self._refresh_history()
#         self._show_page(0)

#     def _build_ui(self):
#         central = QWidget()
#         root = QHBoxLayout(central)
#         root.setContentsMargins(0, 0, 0, 0)
#         root.setSpacing(0)

#         sidebar = QFrame()
#         sidebar.setObjectName("Sidebar")
#         sidebar.setFixedWidth(220)
#         side = QVBoxLayout(sidebar)
#         side.setContentsMargins(18, 24, 18, 18)
#         brand = QLabel("MediaDownloader")
#         brand.setObjectName("Brand")
#         side.addWidget(brand)
#         sub = QLabel("Windows desktop")
#         sub.setObjectName("Muted")
#         side.addWidget(sub)
#         side.addSpacing(30)
#         self.nav_buttons = []
#         for index, label in enumerate(["Home", "Downloads", "History", "Settings"]):
#             button = QPushButton(label)
#             button.setCursor(Qt.PointingHandCursor)
#             button.clicked.connect(lambda checked=False, i=index: self._show_page(i))
#             side.addWidget(button)
#             self.nav_buttons.append(button)
#         side.addStretch()
#         side.addWidget(QLabel("MP3  •  MP4"))
#         root.addWidget(sidebar)

#         content = QWidget()
#         content_layout = QVBoxLayout(content)
#         content_layout.setContentsMargins(28, 24, 28, 24)
#         self.pages = QStackedWidget()
#         self.pages.addWidget(self._build_home())
#         self.pages.addWidget(self._build_downloads())
#         self.pages.addWidget(self._build_history())
#         self.pages.addWidget(self._build_settings())
#         content_layout.addWidget(self.pages)
#         root.addWidget(content, 1)
#         self.setCentralWidget(central)
#         self.statusBar().showMessage("Ready")

#     def _panel(self):
#         frame = QFrame()
#         frame.setObjectName("Panel")
#         layout = QVBoxLayout(frame)
#         layout.setContentsMargins(20, 18, 20, 18)
#         layout.setSpacing(12)
#         return frame, layout

#     def _heading(self, title, subtitle):
#         title_label = QLabel(title)
#         title_label.setObjectName("PageTitle")
#         subtitle_label = QLabel(subtitle)
#         subtitle_label.setObjectName("Muted")
#         return title_label, subtitle_label

#     def _build_home(self):
#         page = QWidget()
#         layout = QVBoxLayout(page)
#         title, subtitle = self._heading("Download media", "Save media you own or have permission to download.")
#         layout.addWidget(title)
#         layout.addWidget(subtitle)
#         panel, form = self._panel()
#         form.addWidget(QLabel("Media URL"))
#         url_row = QHBoxLayout()
#         self.url_input = QLineEdit()
#         self.url_input.setPlaceholderText("Paste a supported media URL here…")
#         self.url_input.returnPressed.connect(self._start_download)
#         paste = QPushButton("Paste")
#         paste.clicked.connect(lambda: self.url_input.setText(
#             self.url_input.text() or __import__("PySide6").QtWidgets.QApplication.clipboard().text()
#         ))
#         url_row.addWidget(self.url_input, 1)
#         url_row.addWidget(paste)
#         form.addLayout(url_row)

#         choice_row = QHBoxLayout()
#         choice_row.addWidget(QLabel("Format"))
#         self.format_combo = QComboBox()
#         self.format_combo.addItems(["MP3 — Audio", "MP4 — Video"])
#         self.format_combo.setCurrentIndex(0 if self.settings["default_format"] == "mp3" else 1)
#         choice_row.addWidget(self.format_combo)
#         choice_row.addSpacing(20)
#         choice_row.addWidget(QLabel("Save to"))
#         self.output_input = QLineEdit(self.settings["download_dir"])
#         browse = QPushButton("Browse")
#         browse.clicked.connect(self._browse_output)
#         choice_row.addWidget(self.output_input, 1)
#         choice_row.addWidget(browse)
#         form.addLayout(choice_row)

#         self.start_button = QPushButton("Start download")
#         self.start_button.setObjectName("Primary")
#         self.start_button.clicked.connect(self._start_download)
#         form.addWidget(self.start_button)
#         layout.addWidget(panel)

#         progress_panel, progress_layout = self._panel()
#         row = QHBoxLayout()
#         row.addWidget(QLabel("Current download"))
#         row.addStretch()
#         self.progress_text = QLabel("Waiting for a URL")
#         self.progress_text.setObjectName("Muted")
#         row.addWidget(self.progress_text)
#         progress_layout.addLayout(row)
#         self.progress_bar = QProgressBar()
#         self.progress_bar.setRange(0, 100)
#         self.progress_bar.setValue(0)
#         progress_layout.addWidget(self.progress_bar)
#         self.progress_details = QLabel("Speed: —    ETA: —")
#         self.progress_details.setObjectName("Muted")
#         progress_layout.addWidget(self.progress_details)
#         action_row = QHBoxLayout()
#         self.cancel_button = QPushButton("Cancel download")
#         self.cancel_button.setObjectName("Danger")
#         self.cancel_button.setEnabled(False)
#         self.cancel_button.clicked.connect(self._cancel_download)
#         action_row.addStretch()
#         action_row.addWidget(self.cancel_button)
#         progress_layout.addLayout(action_row)
#         layout.addWidget(progress_panel)

#         log_panel, log_layout = self._panel()
#         log_layout.addWidget(QLabel("Activity"))
#         self.log_view = QTextEdit()
#         self.log_view.setReadOnly(True)
#         self.log_view.setMinimumHeight(150)
#         log_layout.addWidget(self.log_view)
#         layout.addWidget(log_panel, 1)
#         return page

#     def _build_downloads(self):
#         page = QWidget()
#         layout = QVBoxLayout(page)
#         title, subtitle = self._heading("Downloads", "Your current activity appears on the Home page.")
#         layout.addWidget(title)
#         layout.addWidget(subtitle)
#         panel, inner = self._panel()
#         inner.addWidget(QLabel("Download controls"))
#         self.downloads_status = QLabel("No active download.")
#         inner.addWidget(self.downloads_status)
#         open_folder = QPushButton("Open download folder")
#         open_folder.clicked.connect(self._open_folder)
#         inner.addWidget(open_folder)
#         layout.addWidget(panel)
#         layout.addStretch()
#         return page

#     def _build_history(self):
#         page = QWidget()
#         layout = QVBoxLayout(page)
#         title, subtitle = self._heading("Download history", "Completed and failed download attempts stored on this PC.")
#         layout.addWidget(title)
#         layout.addWidget(subtitle)
#         panel, inner = self._panel()
#         self.history_table = QTableWidget(0, 5)
#         self.history_table.setHorizontalHeaderLabels(["Title", "Format", "Status", "Saved file", "Date"])
#         self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
#         self.history_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
#         self.history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
#         self.history_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
#         inner.addWidget(self.history_table)
#         buttons = QHBoxLayout()
#         refresh = QPushButton("Refresh")
#         refresh.clicked.connect(self._refresh_history)
#         clear = QPushButton("Clear history")
#         clear.clicked.connect(self._clear_history)
#         buttons.addWidget(refresh)
#         buttons.addStretch()
#         buttons.addWidget(clear)
#         inner.addLayout(buttons)
#         layout.addWidget(panel, 1)
#         return page

#     def _build_settings(self):
#         page = QWidget()
#         layout = QVBoxLayout(page)
#         title, subtitle = self._heading("Settings", "Local preferences only. No API keys or account configuration.")
#         layout.addWidget(title)
#         layout.addWidget(subtitle)
#         panel, form = self._panel()
#         form.addWidget(QLabel("Default format"))
#         self.settings_format = QComboBox()
#         self.settings_format.addItems(["MP3", "MP4"])
#         self.settings_format.setCurrentIndex(0 if self.settings["default_format"] == "mp3" else 1)
#         form.addWidget(self.settings_format)
#         form.addWidget(QLabel("MP3 quality"))
#         self.audio_quality = QComboBox()
#         self.audio_quality.addItems(["128", "192", "256", "320"])
#         self.audio_quality.setCurrentText(str(self.settings["audio_quality"]))
#         form.addWidget(self.audio_quality)
#         form.addWidget(QLabel("Maximum MP4 video height"))
#         self.video_quality = QComboBox()
#         self.video_quality.addItems(["360", "480", "720", "1080", "1440", "2160"])
#         self.video_quality.setCurrentText(str(self.settings["video_quality"]))
#         form.addWidget(self.video_quality)
#         self.embed_thumbnail = QCheckBox("Embed available thumbnail in MP3")
#         self.embed_thumbnail.setChecked(bool(self.settings["embed_thumbnail"]))
#         form.addWidget(self.embed_thumbnail)
#         self.fetch_lyrics = QCheckBox("Try to fetch synced lyrics for MP3")
#         self.fetch_lyrics.setChecked(bool(self.settings["fetch_lyrics"]))
#         form.addWidget(self.fetch_lyrics)
#         form.addWidget(QLabel("Theme"))
#         self.theme_combo = QComboBox()
#         self.theme_combo.addItems(["Dark", "Light"])
#         self.theme_combo.setCurrentText(self.settings["theme"].capitalize())
#         form.addWidget(self.theme_combo)
#         save = QPushButton("Save settings")
#         save.setObjectName("Primary")
#         save.clicked.connect(self._save_settings)
#         form.addWidget(save)
#         ffmpeg_label = QLabel(
#             "FFmpeg: " + ("Detected" if find_ffmpeg() else "Not detected — required for MP3 conversion and MP4 merging.")
#         )
#         ffmpeg_label.setObjectName("Muted")
#         form.addWidget(ffmpeg_label)
#         layout.addWidget(panel)
#         layout.addStretch()
#         return page

#     def _apply_theme(self):
#         self.setStyleSheet(DARK_STYLESHEET if self.settings.get("theme") == "dark" else LIGHT_STYLESHEET)

#     def _show_page(self, index):
#         self.pages.setCurrentIndex(index)
#         for i, button in enumerate(self.nav_buttons):
#             button.setProperty("active", i == index)
#         if index == 2:
#             self._refresh_history()

#     def _browse_output(self):
#         folder = QFileDialog.getExistingDirectory(self, "Choose download folder", self.output_input.text())
#         if folder:
#             self.output_input.setText(folder)

#     def _start_download(self):
#         if self.worker and self.worker.isRunning():
#             QMessageBox.information(self, "Download running", "Wait for the current download to finish.")
#             return
#         url = self.url_input.text().strip()
#         if not url:
#             QMessageBox.warning(self, "Missing URL", "Paste a media URL first.")
#             return
#         output = self.output_input.text().strip()
#         if not output:
#             QMessageBox.warning(self, "Missing folder", "Choose a download folder.")
#             return
#         media_format = "mp3" if self.format_combo.currentIndex() == 0 else "mp4"
#         Path(output).mkdir(parents=True, exist_ok=True)
#         self.settings["download_dir"] = output
#         self.settings["default_format"] = media_format
#         save_settings(self.settings)
#         self.log_view.append(f"URL: {url}\nFormat: {media_format.upper()}\nFolder: {output}")
#         self.progress_bar.setValue(0)
#         self.progress_text.setText("Starting…")
#         self.start_button.setEnabled(False)
#         self.cancel_button.setEnabled(True)
#         self.downloads_status.setText(f"Downloading {media_format.upper()}…")
#         self.worker = DownloadWorker(url, media_format, output, self.settings.copy())
#         self.worker.progress.connect(self._on_progress)
#         self.worker.log.connect(self._append_log)
#         self.worker.completed.connect(self._on_completed)
#         self.worker.failed.connect(self._on_failed)
#         self.worker.cancelled.connect(self._on_cancelled)
#         self.worker.finished.connect(self._worker_finished)
#         self.worker.start()

#     def _on_progress(self, percent, speed, eta, filename):
#         self.progress_bar.setValue(percent)
#         self.progress_text.setText(Path(filename).name if filename else f"{percent}%")
#         self.progress_details.setText(f"Speed: {speed or '—'}    ETA: {eta or '—'}")

#     def _append_log(self, message):
#         self.log_view.append(message)
#         self.statusBar().showMessage(message, 5000)

#     def _on_completed(self, title, filepath):
#         self.progress_bar.setValue(100)
#         self.progress_text.setText("Completed")
#         self._append_log(f"Completed: {title}\nSaved: {filepath}")
#         self.downloads_status.setText(f"Completed: {title}")
#         self._refresh_history()
#         QMessageBox.information(self, "Download complete", f"{title}\n\nSaved to:\n{filepath}")

#     def _on_failed(self, error):
#         self.progress_text.setText("Failed")
#         self._append_log(f"ERROR: {error}")
#         self.downloads_status.setText("The download failed.")
#         QMessageBox.critical(self, "Download failed", error)

#     def _on_cancelled(self):
#         self.progress_text.setText("Cancelled")
#         self._append_log("Download cancelled.")
#         self.downloads_status.setText("Download cancelled.")
#         self._refresh_history()

#     def _worker_finished(self):
#         self.start_button.setEnabled(True)
#         self.cancel_button.setEnabled(False)
#         self.worker = None

#     def _cancel_download(self):
#         if self.worker and self.worker.isRunning():
#             self.worker.cancel()
#             self.cancel_button.setEnabled(False)
#             self._append_log("Cancellation requested…")

#     def _open_folder(self):
#         folder = self.output_input.text().strip() or self.settings["download_dir"]
#         Path(folder).mkdir(parents=True, exist_ok=True)
#         QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

#     def _refresh_history(self):
#         if not hasattr(self, "history_table"):
#             return
#         rows = database.get_downloads()
#         self.history_table.setRowCount(len(rows))
#         for r, row in enumerate(rows):
#             values = [row["title"], row["media_format"].upper(), row["status"],
#                       row["output_path"], row["created_at"]]
#             for c, value in enumerate(values):
#                 self.history_table.setItem(r, c, QTableWidgetItem(str(value)))

#     def _clear_history(self):
#         answer = QMessageBox.question(self, "Clear history", "Delete all download history records?")
#         if answer == QMessageBox.Yes:
#             database.clear_history()
#             self._refresh_history()

#     def _save_settings(self):
#         self.settings.update({
#             "default_format": "mp3" if self.settings_format.currentIndex() == 0 else "mp4",
#             "audio_quality": self.audio_quality.currentText(),
#             "video_quality": self.video_quality.currentText(),
#             "embed_thumbnail": self.embed_thumbnail.isChecked(),
#             "fetch_lyrics": self.fetch_lyrics.isChecked(),
#             "theme": self.theme_combo.currentText().lower(),
#         })
#         save_settings(self.settings)
#         self._apply_theme()
#         self._append_log("Settings saved.")
#         QMessageBox.information(self, "Settings", "Your settings have been saved.")
