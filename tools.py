from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QDialog

def disable_escape(event: QKeyEvent|None, dialog: QDialog) -> None:
    if event == None:
        return
    if event.key() == Qt.Key.Key_Escape:
        event.ignore()
    else:
        QDialog.keyPressEvent(dialog, event)