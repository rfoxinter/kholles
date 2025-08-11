from socket import gethostbyname, gethostname
from threading import Thread
from time import sleep
from urllib.request import urlopen

from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QDialog, QVBoxLayout

from httpserver import main_httpserver


class ViewerDialog(QDialog):
    def __init__(self, _parent, file: str):
        super().__init__(parent=_parent)

        self.setWindowTitle("PDF Viewer")
        self.setGeometry(100, 100, 1000, 750)
        self.setModal(True)

        # Layout and WebView
        layout = QVBoxLayout(self)
        self.webView = QWebEngineView()
        layout.addWidget(self.webView)

        # Start server thread
        self.t = Thread(target=main_httpserver)
        self.t.start()

        ip = gethostbyname(gethostname())
        sleep(2)
        pdf_url = f"http://{ip}:8000/web/viewer.html?file=http://{ip}:8000/{file}"

        self.webView.setUrl(QUrl(pdf_url))

        self.exec()

        try:
            urlopen(f"http://{ip}:8000/EXIT_SERVER")
        except:
            pass

        self.t.join()
