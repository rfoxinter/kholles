from datetime import datetime
from os import name
import sys
from time import sleep
if name == "nt":
    from ctypes import windll

from PyQt6.QtWidgets import QApplication

import database
import ui
import zipdb


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    print("An error occurred. Backup files have been created with the previous and current state of the database.", flush=True)
    zipdb.compress(db.bkp.serialize(), f"exercices_{datetime.today().strftime('%Y%m%d%H%M%S')}.old.db.zip")
    zipdb.compress(db.db.serialize(), f"exercices_{datetime.today().strftime('%Y%m%d%H%M%S')}.bkp.db.zip")
sys.excepthook = handle_exception

app = QApplication(sys.argv)    
if name == "nt":
    windll.shell32.SetCurrentProcessExplicitAppUserModelID('ecerciceskholle')
    windll.shcore.SetProcessDpiAwareness(True)
db = database.database_exercices()
em = ui.ExerciseManager(app, db, __file__)
em.show()
exit_code = app.exec()
print("Writing database.")
zipdb.compress(db.db.serialize())
print(f"Exiting with code {exit_code}.")
sleep(5)
sys.exit(exit_code)