import sys
from PySide6.QtWidgets import QApplication
from app.application import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MediaDownloader")
    app.setOrganizationName("MediaDownloader")
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
