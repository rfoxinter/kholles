from datetime import datetime
from os import name
from os.path import dirname
import sys
from time import sleep
from traceback import print_exception
if name == "nt":
    from ctypes import windll

from PyQt6.QtWidgets import QApplication

from database import database_exercices
from ui import exercise_manager
from zipdb import compress

debug = (getattr(sys, 'gettrace', None) == None) or ("debugpy" in sys.modules)

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    if debug:
        print_exception(exc_type, exc_value, exc_traceback)
    else:
        print("An error occurred. Backup files have been created with the previous and current state of the database.", flush=True)
        compress(db.bkp.serialize(), f"exercices_{datetime.today().strftime('%Y%m%d%H%M%S')}.old.db.zip")
        compress(db.db.serialize(), f"exercices_{datetime.today().strftime('%Y%m%d%H%M%S')}.bkp.db.zip")
sys.excepthook = handle_exception

app = QApplication(sys.argv)    
if name == "nt":
    windll.shell32.SetCurrentProcessExplicitAppUserModelID('ecerciceskholle')
    windll.shcore.SetProcessDpiAwareness(True)
db = database_exercices()
em = exercise_manager(app, db, dirname(__file__))
em.show()
exit_code = app.exec()
if not debug:
    print("Writing database.")
    print(f"Compression rate of {int(100 * compress(db.db.serialize()) + 0.5)}%.")
print(f"Exiting with code {exit_code}.")
if not debug:
    sleep(5)
sys.exit(exit_code)