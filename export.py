from base64 import b64decode, b64encode
from typing import TYPE_CHECKING
from unicodedata import normalize
from zipfile import ZIP_LZMA, ZipFile

from PyQt6.QtWidgets import QComboBox, QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QRadioButton, QVBoxLayout

from exercises import database_exercices
if TYPE_CHECKING:
    from ui import exercise_manager

def first_upper(s: str) -> str:
    return s[:1].upper() + s[1:]

def resolve_unknown_dialog(parent, unknown_value: str, existing_values: list[str], unknown_type: str, unknown_prefix: str, unknown_masculin: bool) -> tuple[str, int]:
    dialog = QDialog(parent)
    dialog.setWindowTitle(f"{first_upper(unknown_type)} inconnue")
    dialog.setModal(True)
    dialog.setStyleSheet("background-color: #121212; color: white;")

    layout = QVBoxLayout(dialog)

    # Instruction label
    label = QLabel(f"{first_upper(unknown_prefix)}{unknown_type} «\u00A0{unknown_value}\u00A0» est inconnue.")
    label.setStyleSheet("font-size: 14px;")
    layout.addWidget(label)

    # Option 1: Ignore
    radio_ignore = QRadioButton(f"Ignorer {unknown_prefix}{unknown_type}")
    radio_ignore.setStyleSheet("font-size: 13px;")
    layout.addWidget(radio_ignore)

    # Option 2: Add new value (text input)
    radio_add = QRadioButton(f"Ajouter un{'e' if not unknown_masculin else ''} nouve{'lle' if not unknown_masculin else 'au'} {unknown_type}")
    radio_add.setStyleSheet("font-size: 13px;")
    layout.addWidget(radio_add)

    input_new_value = QLineEdit()
    input_new_value.setText(unknown_value)
    input_new_value.setEnabled(False)
    input_new_value.setStyleSheet("background-color: #333; color: white; font-size: 14px;")
    layout.addWidget(input_new_value)

    # Option 3: Match with existing value (dropdown)
    radio_match = QRadioButton(f"Associer à un{'e' if not unknown_masculin else ''} {unknown_type} existante")
    radio_match.setStyleSheet("font-size: 13px;")
    layout.addWidget(radio_match)

    combo_existing_values = QComboBox()
    combo_existing_values.addItems(existing_values)
    combo_existing_values.setEnabled(False)
    combo_existing_values.setStyleSheet("background-color: #333; color: white; font-size: 14px;")
    layout.addWidget(combo_existing_values)

    # When a radio button is toggled, enable the appropriate input
    def update_inputs():
        input_new_value.setEnabled(radio_add.isChecked())
        combo_existing_values.setEnabled(radio_match.isChecked())

    radio_ignore.toggled.connect(update_inputs)
    radio_add.toggled.connect(update_inputs)
    radio_match.toggled.connect(update_inputs)

    # Buttons at the bottom
    btn_layout = QHBoxLayout()

    btn_ok = QPushButton("Valider")
    btn_ok.setStyleSheet("background-color: #006600; color: white; padding: 8px; border-radius: 6px;")

    btn_layout.addWidget(btn_ok)
    layout.addLayout(btn_layout)

    result = {"choice": ("",0)}

    def close() -> None:
        if radio_ignore.isChecked():
            result["choice"] = ("",0)
        elif radio_add.isChecked():
            result["choice"] = (input_new_value.text().strip(), 1)
        elif radio_match.isChecked():
            result["choice"] = (combo_existing_values.currentText(), 2)
        dialog.close()

    btn_ok.clicked.connect(close)

    radio_add.setChecked(True)  # Default selected option
    update_inputs()  # Enable corresponding field

    dialog.exec()
    return result["choice"]



def export_ex(db: database_exercices, flnm: str, exs: list[int]) -> None:
    file = ZipFile(flnm, "w", compression=ZIP_LZMA, compresslevel=9)
    for i, ex in enumerate(exs):
        _, name, diff, exer, ans, year, req_chap, chap = db.get_exercise(ex)
        ex_data = b64encode(name.encode("utf-8")).decode("utf-8") + "\n"
        ex_data += b64encode(str(diff).encode("utf-8")).decode("utf-8") + "\n"
        ex_data += b64encode(exer.encode("utf-8")).decode("utf-8") + "\n"
        ex_data += b64encode(ans.encode("utf-8")).decode("utf-8") + "\n"
        years = list(map(int,filter(lambda x: x != "", year.split(","))))
        ex_data += str(len(years)) + "\n"
        for y in years:
            ex_data += b64encode(db.get_year_name(y).encode("utf-8")).decode("utf-8") + "\n"
        req_chaps = list(map(int,filter(lambda x: x != "", req_chap.split(","))))
        ex_data += str(len(req_chaps)) + "\n"
        for rc in req_chaps:
            ex_data += b64encode(db.get_chapter(rc).encode("utf-8")).decode("utf-8") + "\n"
        chaps = list(map(int,filter(lambda x: x != "", chap.split(","))))
        ex_data += str(len(chaps)) + "\n"
        for c in chaps:
            ex_data += b64encode(db.get_chapter(c).encode("utf-8")).decode("utf-8") + "\n"
        file.writestr(str(i),ex_data)
    file.close()

def import_ex(manager: 'exercise_manager', db: database_exercices, flnm: str) -> None:
    myzip = ZipFile(flnm, "r", compression=ZIP_LZMA, compresslevel=9)
    for file in myzip.filelist:
        exercise = myzip.open(file)
        title = b64decode(exercise.readline().strip()).decode("utf-8")
        difficulty = int(b64decode(exercise.readline().strip())) + 6
        ex_data = b64decode(exercise.readline().strip()).decode("utf-8")
        answer = b64decode(exercise.readline().strip()).decode("utf-8")
        nb_years = int(exercise.readline().strip())
        years = []
        for _ in range(nb_years):
            year_str = b64decode(exercise.readline().strip()).decode("utf-8")
            try:
                years.append(db.get_year_id(year_str))
            except IndexError:
                val, res = resolve_unknown_dialog(manager, year_str, sorted(db.list_chapter_names(), key=lambda s: normalize("NFD", s)), "année", "l\u2019", True)
                if res == 1:
                    db.add_year(val, len(db.list_years()))
                if res != 0:
                    years.append(db.get_year_id(val))
        nb_req_chaps = int(exercise.readline().strip())
        req_chaps = []
        for _ in range(nb_req_chaps):
            req_chap_str = b64decode(exercise.readline().strip()).decode("utf-8")
            try:
                req_chaps.append(db.get_chapter_id(req_chap_str))
            except IndexError:
                val, res = resolve_unknown_dialog(manager, req_chap_str, sorted(db.list_chapter_names(), key=lambda s: normalize("NFD", s)), "année", "l\u2019", True)
                if res == 1:
                    db.add_chapter(val)
                if res != 0:
                    req_chaps.append(db.get_chapter_id(val))
        nb_chaps = int(exercise.readline().strip())
        chaps = []
        for _ in range(nb_chaps):
            chap_str = b64decode(exercise.readline().strip()).decode("utf-8")
            try:
                chaps.append(db.get_chapter_id(chap_str))
            except IndexError:
                val, res = resolve_unknown_dialog(manager, chap_str, sorted(db.list_chapter_names(), key=lambda s: normalize("NFD", s)), "année", "l\u2019", True)
                if res == 1:
                    db.add_chapter(val)
                if res != 0:
                    chaps.append(db.get_chapter_id(val))
        manager.open_add_exercise_window(lambda _, b, c, d, e, f, g, h: db.add_exercise(b, c, d, e, f, g, h), -1, title, difficulty, ex_data, answer, years, chaps, req_chaps)