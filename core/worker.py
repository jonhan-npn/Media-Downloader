import threading
from PySide6.QtCore import QThread, Signal
from core.downloader import MediaDownloader, DownloadCancelled
from storage.database import add_download

class DownloadWorker(QThread):
    progress = Signal(int, str, str, str)
    log = Signal(str)
    completed = Signal(str, str)
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self, url, media_format, output_dir, settings):
        super().__init__()
        self.url = url
        self.media_format = media_format
        self.output_dir = output_dir
        self.settings = settings
        self.cancel_event = threading.Event()

    def cancel(self):
        self.cancel_event.set()

    def run(self):
        engine = MediaDownloader(
            self.progress.emit, self.log.emit, self.cancel_event, self.settings
        )
        title = "Unknown media"
        filepath = self.output_dir
        status = "failed"
        try:
            title, filepath = engine.download(
                self.url, self.media_format, self.output_dir
            )
            status = "completed"
            add_download(title, self.url, self.media_format, filepath, status)
            self.completed.emit(title, filepath)
        except DownloadCancelled:
            status = "cancelled"
            add_download(title, self.url, self.media_format, filepath, status)
            self.cancelled.emit()
        except Exception as exc:
            add_download(title, self.url, self.media_format, filepath, status)
            self.failed.emit(str(exc))
