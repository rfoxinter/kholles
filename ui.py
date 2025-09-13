from math import nan
from os import chdir, name, system
from os.path import basename, split, splitext
from re import match, sub
from time import sleep
from unicodedata import normalize
from warnings import warn

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QStandardItem, QStandardItemModel
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QAbstractSpinBox,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtWidgets import QHBoxLayout
from superqt.utils import CodeSyntaxHighlight

from database import database_exercices
from exercises import get_exercises
from export import export_ex, import_ex
from latex import gen_book, gen_exercise_book, gen_recap, generate_exercise_sheet
from monokaipp import MonokaiPlusPlusStyle
from pdf_viewer import ViewerDialog
from tools import clean_LaTeX, disable_escape
from zipdb import compress

class normalised_str(QListWidgetItem):
    def __lt__(self, other):
        return normalize("NFD", self.text()) < normalize("NFD", other.text())

class exercise_manager(QWidget):
    def __init__(self, app: QApplication, db: database_exercices, file_dir: str, debug: bool):
        super().__init__()
        self.debug = debug
        self.db = db
        self.app = app
        self.file_dir = file_dir
        QFontDatabase.addApplicationFont('fonts/Stars.ttf')
        QFontDatabase.addApplicationFont('fonts/Ubuntu-Regular.ttf')
        QFontDatabase.addApplicationFont('fonts/UbuntuMono-Regular.ttf')
        QFontDatabase.addApplicationFont('fonts/UbuntuMono-Bold.ttf')
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Exercise Manager")
        self.setGeometry(100, 100, 350, 350)
        self.setStyleSheet("font-family: 'Ubuntu'; font-size: 12px; background-color: #0d0d0d;")
        self.setWindowIcon(QIcon("favicon.ico"))
        self.setStyleSheet("""
            QScrollBar:vertical, QScrollBar:horizontal {
                width: 0px;
                height: 0px;
                background: transparent;
            }
        """)

        
        layout = QVBoxLayout()
        buttons = [
            ("Ajouter un exercice", lambda: self.open_add_exercise_window(lambda _, b, c, d, e, f, g, h: self.db.add_exercise(b, c, d, e, f, g, h))),
            ("Modifier un exercice", self.open_edit_exercise_window),
            ("Gérer les années", self.open_manage_years_window),
            ("Gérer les chapitres", self.open_manage_chaps_window),
            ("Générer une feuille d\u2019exercices", self.gen_exercises),
            ("Visualiser les exercices", self.gen_book),
            ("Exporter des exercices", self.export_exercises),
            ("Importer des exercices", self.import_exercises),
            ("Sauvegarder la base de données", lambda: self.open_window("Sauvegarde de la base de données", ["Sauvegarde effectuée.", f"Base de données compressée à {int(100 * compress(self.db.db.serialize()) + 0.5)}%."]))
        ]
        
        for text, handler in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(
                "background-color: #003366; color: white; font-size: 14px; padding: 10px; border-radius: 10px;"
            )
            btn.clicked.connect(lambda checked, h=handler: h())
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(btn)
            
        self.setLayout(layout)

    def open_add_exercise_window(self, add_func, _id: int = -1, ex_name: str = "", ex_diff: int = 6, ex_exr: str = "", ex_ans: str = "", ex_year: list[int] = [], ex_chap: list[int] = [], ex_req_chap: list[int] = []):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter un exercice")
        dialog.setStyleSheet("font-family: 'Ubuntu'; font-size: 12px;  background-color: #121212;")
        dialog.setWindowIcon(QIcon("favicon.ico"))
        dialog.setModal(True)
        dialog.keyPressEvent = lambda a0: disable_escape(a0, dialog)
        
        layout = QVBoxLayout(dialog)
        
        title_input = QPlainTextEdit()
        title_input.setPlainText(ex_name)
        title_input.setFixedHeight(30)
        title_input.setStyleSheet("background-color: #333; color: white; font-size: 14px;")
        title_input.setPlaceholderText('Nom de l\u2019exercice')
        layout.addWidget(title_input)

        difficulty_selector = QComboBox()
        labels = ['B.', 'D.', 'E.', 'F.', 'G.', 'H.', 'B', 'D', 'E', 'F', 'G', 'H']
        model = QStandardItemModel()
        if name == "nt":
            for i, label in enumerate(labels):
                item = QStandardItem(label)
                if i < 6:
                    item.setForeground(Qt.GlobalColor.cyan)
                else:
                    item.setForeground(Qt.GlobalColor.white)
                model.appendRow(item)
        else:
            for i, label in enumerate(labels):
                item = QStandardItem(label)
                if i < 6:
                    item.setForeground(Qt.GlobalColor.cyan)
                    item.setBackground(Qt.GlobalColor.darkCyan)
                else:
                    item.setForeground(Qt.GlobalColor.white)
                    item.setBackground(Qt.GlobalColor.darkGray)
                model.appendRow(item)

        difficulty_selector.setModel(model)
        difficulty_selector.setCurrentIndex(ex_diff if ex_diff != None else 6)

        # Base style
        base_style = """
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: transparent;
            }
            QComboBox::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: transparent;
                border-right: transparent;
                border-top: 10px solid white;
                margin-right: 5px;
            }
            QComboBox {
                font-family: stars;
                background-color: #333;
                font-size: 25px;
        """

        # Update text color in the display area
        def update_text_color(index):
            if index < 6:
                difficulty_selector.setStyleSheet(base_style + " color: cyan;}")
            else:
                difficulty_selector.setStyleSheet(base_style + " color: white;}")

        difficulty_selector.currentIndexChanged.connect(update_text_color)
        update_text_color(difficulty_selector.currentIndex())  # Set initial color

        layout.addWidget(difficulty_selector)
        
        # Exercise        
        exercise_input = QPlainTextEdit()
        exercise_input.setPlainText(ex_exr)
        exercise_input.setMinimumHeight(200)
        exercise_input.setStyleSheet("background-color: #333; color: white; font-size: 14px;")
        exercise_input.setPlaceholderText('Exercice')
        exercise_input.setStyleSheet("font-family: 'Ubuntu Mono'; font-size: 14px;  background-color: #121212;")
        self.e_highlighter = CodeSyntaxHighlight(exercise_input.document(), "latex", MonokaiPlusPlusStyle)
        layout.addWidget(exercise_input)
        
        # Answer
        answer_input = QPlainTextEdit()
        answer_input.setPlainText(ex_ans)
        answer_input.setMinimumHeight(150)
        answer_input.setStyleSheet("background-color: #333; color: white; font-size: 14px;")
        answer_input.setPlaceholderText('Réponse')
        answer_input.setStyleSheet("font-family: 'Ubuntu Mono'; font-size: 14px;  background-color: #121212;")
        self.a_highlighter = CodeSyntaxHighlight(answer_input.document(), "latex", MonokaiPlusPlusStyle)
        layout.addWidget(answer_input)

        
        
        def populate_year_options(options):
            """Populate the left list with sorted options"""
            for option in sorted(options, key=lambda s: normalize("NFD", s)):  # Ensure initial sorting
                item = QListWidgetItem(option)
                year_list_unselected.addItem(normalised_str(item))

        def move_year_to_selected(item):
            """Move item from unselected to selected list and keep sorting"""
            year_list_unselected.takeItem(year_list_unselected.row(item))
            year_list_selected.addItem(normalised_str(item))
            year_list_selected.sortItems()  # Keep sorted
            year_list_unselected.clearSelection()

        def move_year_to_unselected(item):
            """Move item from selected to unselected list and keep sorting"""
            year_list_selected.takeItem(year_list_selected.row(item))
            year_list_unselected.addItem(normalised_str(item))
            year_list_unselected.sortItems()  # Keep sorted
            year_list_selected.clearSelection()

        def get_year_selected_items():
            """Get the items currently in the selected list"""
            selected_items = []
            for index in range(year_list_selected.count()):
                item = year_list_selected.item(index)
                if item != None:
                    selected_items.append(item.text())  # Add item text to the list
            return selected_items

        
        year_layout = QHBoxLayout()

        # Left List (Unselected options)
        year_list_unselected = QListWidget()
        year_list_unselected.setFixedHeight(50)
        year_list_unselected.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        year_list_unselected.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)  # Smooth scrolling
        year_list_unselected.itemDoubleClicked.connect(move_year_to_selected)
        year_list_unselected.setStyleSheet("background-color: #333; color: white; font-size: 14px;")
        year_list_unselected.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        year_layout.addWidget(year_list_unselected)

        # Right List (Selected options)
        year_list_selected = QListWidget()
        year_list_selected.setFixedHeight(50)
        year_list_selected.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        year_list_selected.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)  # Smooth scrolling
        year_list_selected.itemDoubleClicked.connect(move_year_to_unselected)
        year_list_selected.setStyleSheet("background-color: #333; color: white; font-size: 14px;")
        year_list_selected.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        year_layout.addWidget(year_list_selected)

        # Populate the left list with sample options
        populate_year_options(self.db.list_year_names())

        layout.addLayout(year_layout)
        
        if ex_year != []:
            for index in range(year_list_unselected.count()-1, -1, -1):
                item = year_list_unselected.item(index)
                assert item != None
                if self.db.get_year_id(item.text()) in ex_year:
                    move_year_to_selected(item)

        
        
        def populate_chap_options(options):
            """Populate the left list with sorted options"""
            for option in sorted(options, key=lambda s: normalize("NFD", s)):  # Ensure initial sorting
                item = QListWidgetItem(option)
                chap_list_unselected.addItem(normalised_str(item))

        def move_chap_to_selected(item):
            """Move item from unselected to selected list and keep sorting"""
            chap_list_unselected.takeItem(chap_list_unselected.row(item))
            chap_list_selected.addItem(normalised_str(item))
            chap_list_selected.sortItems()  # Keep sorted
            chap_list_unselected.clearSelection()

        def move_chap_to_unselected(item):
            """Move item from selected to unselected list and keep sorting"""
            chap_list_selected.takeItem(chap_list_selected.row(item))
            chap_list_unselected.addItem(normalised_str(item))
            chap_list_unselected.sortItems()  # Keep sorted
            chap_list_selected.clearSelection()

        def get_chap_selected_items():
            """Get the items currently in the selected list"""
            selected_items = []
            for index in range(chap_list_selected.count()):
                item = chap_list_selected.item(index)
                if item != None:
                    selected_items.append(item.text())  # Add item text to the list
            return selected_items
        
        chap_layout = QHBoxLayout()

        # Left List (Unselected options)
        chap_list_unselected = QListWidget()
        chap_list_unselected.setFixedHeight(75)
        chap_list_unselected.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        chap_list_unselected.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)  # Smooth scrolling
        chap_list_unselected.itemDoubleClicked.connect(move_chap_to_selected)
        chap_list_unselected.setStyleSheet("background-color: #333; color: white; font-size: 14px;")
        chap_list_unselected.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        chap_layout.addWidget(chap_list_unselected)

        # Right List (Selected options)
        chap_list_selected = QListWidget()
        chap_list_selected.setFixedHeight(75)
        chap_list_selected.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        chap_list_selected.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)  # Smooth scrolling
        chap_list_selected.itemDoubleClicked.connect(move_chap_to_unselected)
        chap_list_selected.setStyleSheet("background-color: #333; color: white; font-size: 14px;")
        chap_list_selected.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        chap_layout.addWidget(chap_list_selected)

        # Populate the left list with sample options
        populate_chap_options(self.db.list_chapter_names())

        layout.addLayout(chap_layout)
        
        if ex_chap != []:
            for index in range(chap_list_unselected.count()-1, -1, -1):
                item = chap_list_unselected.item(index)
                assert item != None
                if self.db.get_chapter_id(item.text()) in ex_chap:
                    move_chap_to_selected(item)

        
        
        def populate_req_chap_options(options):
            """Populate the left list with sorted options"""
            for option in sorted(options, key=lambda s: normalize("NFD", s)):  # Ensure initial sorting
                item = QListWidgetItem(option)
                req_chap_list_unselected.addItem(normalised_str(item))

        def move_req_chap_to_selected(item):
            """Move item from unselected to selected list and keep sorting"""
            req_chap_list_unselected.takeItem(req_chap_list_unselected.row(item))
            req_chap_list_selected.addItem(normalised_str(item))
            req_chap_list_selected.sortItems()  # Keep sorted
            req_chap_list_unselected.clearSelection()

        def move_req_chap_to_unselected(item):
            """Move item from selected to unselected list and keep sorting"""
            req_chap_list_selected.takeItem(req_chap_list_selected.row(item))
            req_chap_list_unselected.addItem(normalised_str(item))
            req_chap_list_unselected.sortItems()  # Keep sorted
            req_chap_list_selected.clearSelection()

        def get_req_chap_selected_items():
            """Get the items currently in the selected list"""
            selected_items = []
            for index in range(req_chap_list_selected.count()):
                item = req_chap_list_selected.item(index)
                if item != None:
                    selected_items.append(item.text())  # Add item text to the list
            return selected_items
        
        req_chap_layout = QHBoxLayout()

        # Left List (Unselected options)
        req_chap_list_unselected = QListWidget()
        req_chap_list_unselected.setFixedHeight(75)
        req_chap_list_unselected.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        req_chap_list_unselected.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)  # Smooth scrolling
        req_chap_list_unselected.itemDoubleClicked.connect(move_req_chap_to_selected)
        req_chap_list_unselected.setStyleSheet("background-color: #333; color: white; font-size: 14px;")
        req_chap_list_unselected.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        req_chap_layout.addWidget(req_chap_list_unselected)

        # Right List (Selected options)
        req_chap_list_selected = QListWidget()
        req_chap_list_selected.setFixedHeight(75)
        req_chap_list_selected.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        req_chap_list_selected.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)  # Smooth scrolling
        req_chap_list_selected.itemDoubleClicked.connect(move_req_chap_to_unselected)
        req_chap_list_selected.setStyleSheet("background-color: #333; color: white; font-size: 14px;")
        req_chap_list_selected.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        req_chap_layout.addWidget(req_chap_list_selected)

        # Populate the left list with sample options
        populate_req_chap_options(self.db.list_chapter_names())

        layout.addLayout(req_chap_layout)
        
        if ex_req_chap != []:
            for index in range(req_chap_list_unselected.count()-1, -1, -1):
                item = req_chap_list_unselected.item(index)
                assert item != None
                if self.db.get_chapter_id(item.text()) in ex_req_chap:
                    move_req_chap_to_selected(item)
        
        # Create a horizontal layout for buttons
        button_layout = QHBoxLayout()

        def add_exercise() -> None:
            years = list(map(lambda x: self.db.get_year_id(x), get_year_selected_items()))
            chaps = list(map(lambda x: self.db.get_chapter_id(x), get_chap_selected_items()))
            req_chaps = list(map(lambda x: self.db.get_chapter_id(x), get_req_chap_selected_items()))
            diff = ['B.', 'D.', 'E.', 'F.', 'G.', 'H.', 'B', 'D', 'E', 'F', 'G', 'H'].index(difficulty_selector.currentText()) - 6
            add_func(_id, title_input.toPlainText(), diff, exercise_input.toPlainText(), answer_input.toPlainText(), years, req_chaps, chaps)
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Ajouter un exercice")
            dlg.setText("Ajout/modification effectué(e)")
            button = dlg.exec()

            dialog.accept()

        # Add Exercise Button on the left
        btn_add_exercise = QPushButton("Ajouter/Modifier l\u2019exercice")
        btn_add_exercise.setStyleSheet("background-color: #003366; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        btn_add_exercise.clicked.connect(add_exercise)  # Connect to the function you want for adding an exercise
        btn_add_exercise.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(btn_add_exercise)

        # Cancel Button on the right
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setStyleSheet("background-color: #a30000; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        btn_cancel.clicked.connect(dialog.close)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(btn_cancel)

        # Add the horizontal button layout to the main layout
        layout.addLayout(button_layout)

        
        dialog.showMaximized()

    def open_edit_exercise_window(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Modifier un exercice")
        dialog.setStyleSheet("background-color: #121212;")
        dialog.setWindowIcon(QIcon("favicon.ico"))
        dialog.setModal(True)
        dialog.keyPressEvent = lambda a0: disable_escape(a0, dialog)

        layout = QVBoxLayout(dialog)

        # Integer Selector
        exercise_selector = QSpinBox()
        exercise_selector.setMinimumHeight(25)
        exercise_selector.setMinimumWidth(250)
        exercise_selector.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        exercise_selector.setMinimum(1)
        exercise_selector.setMaximum(self.db.max_exercises())
        exercise_selector.clear()
        exercise_selector.setStyleSheet("background-color: #333; color: white; font-size: 14px; padding: 5px;")
        layout.addWidget(exercise_selector)

        # Create a horizontal layout for buttons
        button_layout = QHBoxLayout()

        def open_exercise():
            x = self.db.get_exercise(exercise_selector.value())
            self.open_add_exercise_window(self.db.update_exercise, x[0], x[1], x[2] + 6, x[3], x[4], list(map(int,filter(lambda x: x != "", x[5].split(',')))), list(map(int,filter(lambda x: x != "", x[7].split(',')))), list(map(int,filter(lambda x: x != "", x[6].split(',')))))

        # Edit Button (Left)
        btn_edit = QPushButton("Modifier l\u2019exercice")
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setStyleSheet("background-color: #003366; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        btn_edit.clicked.connect(lambda: [dialog.close(), open_exercise()])
        button_layout.addWidget(btn_edit)

        # Cancel Button (Right)
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("background-color: #a30000; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        btn_cancel.clicked.connect(dialog.close)
        button_layout.addWidget(btn_cancel)

        # Add button layout to main layout
        layout.addLayout(button_layout)

        dialog.exec()

    def open_manage_years_window(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Gestion des années")
        dialog.setStyleSheet("background-color: #121212; color: white;")
        dialog.setModal(True)
        dialog.keyPressEvent = lambda a0: disable_escape(a0, dialog)

        layout = QVBoxLayout(dialog)

        # List of Years
        year_list = QListWidget()
        year_list.addItems(sorted(self.db.list_year_names(), key=lambda s: normalize("NFD", s)))
        year_list.setStyleSheet("background-color: #333; color: white; font-size: 14px;")
        layout.addWidget(year_list)

        # Text Input for Year Name
        input_field = QLineEdit()
        input_field.setPlaceholderText("Nom de l\u2019année")
        input_field.setStyleSheet("background-color: #333; color: white; font-size: 14px; padding: 5px;")
        layout.addWidget(input_field)

        # Buttons Layout
        btn_layout = QHBoxLayout()

        # Add Year Button
        btn_add = QPushButton("Ajouter l\u2019année")
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setStyleSheet("background-color: #003366; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        btn_layout.addWidget(btn_add)

        # Edit Year Button
        btn_edit = QPushButton("Modifier l\u2019année")
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setStyleSheet("background-color: #555500; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        btn_layout.addWidget(btn_edit)

        # Delete Year Button
        btn_delete = QPushButton("Supprimer l\u2019année")
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete.setStyleSheet("background-color: #a30000; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        btn_layout.addWidget(btn_delete)

        layout.addLayout(btn_layout)

        # Close Button
        btn_close = QPushButton("Fermer")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("background-color: #222; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        btn_close.clicked.connect(dialog.close)
        layout.addWidget(btn_close)

        # --- Logic Functions ---

        def refresh_year_list():
            year_list.clear()
            year_list.addItems(sorted(self.db.list_year_names(), key=lambda s: normalize("NFD", s)))

        def add_year():
            name = input_field.text().strip()
            if name:
                self.db.add_year(name)
                refresh_year_list()
                input_field.clear()

        def edit_year():
            selected = year_list.currentItem()
            if selected:
                old_name = selected.text()
                new_name = input_field.text().strip()
                if new_name:
                    self.db.update_year(old_name, new_name)
                    refresh_year_list()
                    input_field.clear()

        def delete_year():
            selected = year_list.currentItem()
            if selected:
                year_name = selected.text()
                self.db.delete_year(year_name)
                refresh_year_list()

        # --- Connect Buttons ---
        btn_add.clicked.connect(add_year)
        btn_edit.clicked.connect(edit_year)
        btn_delete.clicked.connect(delete_year)

        dialog.exec()

    def open_manage_chaps_window(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Gestion des chapitres")
        dialog.setStyleSheet("background-color: #121212; color: white;")
        dialog.setModal(True)
        dialog.keyPressEvent = lambda a0: disable_escape(a0, dialog)

        layout = QVBoxLayout(dialog)

        # List of Chaps
        chap_list = QListWidget()
        chap_list.addItems(sorted(self.db.list_chapter_names(), key=lambda s: normalize("NFD", s)))
        chap_list.setStyleSheet("background-color: #333; color: white; font-size: 14px;")
        layout.addWidget(chap_list)

        # Text Input for Chap Name
        input_field = QLineEdit()
        input_field.setPlaceholderText("Nom de le chapitre")
        input_field.setStyleSheet("background-color: #333; color: white; font-size: 14px; padding: 5px;")
        layout.addWidget(input_field)

        # Buttons Layout
        btn_layout = QHBoxLayout()

        # Add Chap Button
        btn_add = QPushButton("Ajouter le chapitre")
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setStyleSheet("background-color: #003366; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        btn_layout.addWidget(btn_add)

        # Edit Chap Button
        btn_edit = QPushButton("Modifier le chapitre")
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setStyleSheet("background-color: #555500; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        btn_layout.addWidget(btn_edit)

        # Delete Chap Button
        btn_delete = QPushButton("Supprimer le chapitre")
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete.setStyleSheet("background-color: #a30000; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        btn_layout.addWidget(btn_delete)

        layout.addLayout(btn_layout)

        # Close Button
        btn_close = QPushButton("Fermer")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("background-color: #222; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        btn_close.clicked.connect(dialog.close)
        layout.addWidget(btn_close)

        # --- Logic Functions ---

        def refresh_chap_list():
            chap_list.clear()
            chap_list.addItems(sorted(self.db.list_chapter_names(), key=lambda s: normalize("NFD", s)))

        def add_chap():
            name = input_field.text().strip()
            if name:
                self.db.add_chapter(name)
                refresh_chap_list()
                input_field.clear()

        def edit_chap():
            selected = chap_list.currentItem()
            if selected:
                old_name = selected.text()
                new_name = input_field.text().strip()
                if new_name:
                    self.db.update_chapter(old_name, new_name)
                    refresh_chap_list()
                    input_field.clear()

        def delete_chap():
            selected = chap_list.currentItem()
            if selected:
                chap_name = selected.text()
                self.db.delete_chapter(chap_name)
                refresh_chap_list()

        # --- Connect Buttons ---
        btn_add.clicked.connect(add_chap)
        btn_edit.clicked.connect(edit_chap)
        btn_delete.clicked.connect(delete_chap)

        dialog.exec()

    def gen_exercises(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Modifier un exercice")
        dialog.setStyleSheet("background-color: #121212;")
        dialog.setWindowIcon(QIcon("favicon.ico"))
        dialog.setModal(True)
        dialog.keyPressEvent = lambda a0: disable_escape(a0, dialog)

        layout = QVBoxLayout(dialog)

        # Edit Button (Left)
        btn_none = QPushButton("Générer une feille d\u2019exercices")
        btn_none.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_none.setStyleSheet("background-color: #003366; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        btn_none.clicked.connect(lambda: [dialog.close(), self.gen_exercises_none()])
        layout.addWidget(btn_none)

        btn_with = QPushButton("Générer une feille depuis un fichier")
        btn_with.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_with.setStyleSheet("background-color: #003366; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        btn_with.clicked.connect(lambda: [dialog.close(), self.gen_exercises_with()])
        layout.addWidget(btn_with)

        # Cancel Button (Right)
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("background-color: #a30000; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        btn_cancel.clicked.connect(dialog.close)
        layout.addWidget(btn_cancel)

        dialog.exec()

    def gen_exercises_none(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Générer une feuille d’exercices")
        dialog.setStyleSheet("background-color: #121212;")
        dialog.setWindowIcon(QIcon("favicon.ico"))
        dialog.setModal(True)
        dialog.keyPressEvent = lambda a0: disable_escape(a0, dialog)

        layout = QVBoxLayout(dialog)

        spinboxes = []

        for i in range(1, 4):
            label = QLabel(f"Exercices de l\u2019élève {i}")
            label.setStyleSheet("color: white; font-size: 14px;")
            layout.addWidget(label)

            input_field = QLineEdit()
            input_field.setPlaceholderText(f"Exercices de l\u2019élève {i}")
            input_field.setStyleSheet("background-color: #333; color: white; font-size: 14px; padding: 8px; border-radius: 5px;")
            spinboxes.append(input_field)
            layout.addWidget(input_field)



        # Destination selection
        dest_button = QPushButton("Destination")
        dest_button.setCursor(Qt.CursorShape.PointingHandCursor)
        dest_button.setMaximumWidth(350)
        dest_button.setStyleSheet("background-color: #555; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        layout.addWidget(dest_button)

        dest_path = {"path": ""}  # Mutable to capture path from inner scope

        def choose_destination():
            file_path, _ = QFileDialog.getSaveFileName(dialog, "Choisir le fichier", "", "LaTeX files (*.tex)")
            if file_path:
                dest_path["path"] = file_path
                dest_button.setText(f"Destination: {file_path}")

        dest_button.clicked.connect(choose_destination)

        # Action Buttons (Preview / Compile / Cancel)
        button_layout = QHBoxLayout()

        btn_preview = QPushButton("Prévisualiser la feuille")
        btn_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_preview.setStyleSheet("background-color: #336600; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        button_layout.addWidget(btn_preview)

        btn_compile = QPushButton("Compiler")
        btn_compile.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_compile.setStyleSheet("background-color: #003366; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        button_layout.addWidget(btn_compile)

        btn_cancel = QPushButton("Annuler")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("background-color: #a30000; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        btn_cancel.clicked.connect(dialog.close)
        button_layout.addWidget(btn_cancel)

        layout.addLayout(button_layout)

        # Example slot wiring (add real logic here)
        def preview_sheet():
            generate_exercise_sheet(get_exercises(self.db, spinboxes[0].text()), get_exercises(self.db, spinboxes[1].text()), get_exercises(self.db, spinboxes[2].text()), len(str(self.db.max_exercises())), dest_path["path"], True)
            btn_preview.setText("Compilation en cours")
            self.app.processEvents()
            try:
                folder, file = split(dest_path['path'])
                chdir(folder)
                system(f"pdflatex -interaction=nonstopmode -file-line-error {file}")
                sleep(1)
                if not match(r".tex:[0-9]+:", open(splitext(file)[0] + ".log", "r", encoding="utf-8").read()):
                    chdir(self.file_dir)
                    system(f"copy \"{sub("/", "\\\\", dest_path['path']).replace(".tex", ".pdf")}\" _file.pdf")
                    btn_preview.setText("Prévisualiser la feuille")
                    ViewerDialog(self, "_file.pdf")
                else:
                    warn("The LaTeX compilation terminated with an error.")
            except:
                btn_preview.setText("Une erreur est survenue")
            chdir(self.file_dir)
                

        def compile_sheet():
            generate_exercise_sheet(get_exercises(self.db, spinboxes[0].text()), get_exercises(self.db, spinboxes[1].text()), get_exercises(self.db, spinboxes[2].text()), len(str(self.db.max_exercises())), dest_path["path"])
            btn_compile.setText("Compilation en cours")
            self.app.processEvents()
            try:
                folder, file = split(dest_path['path'])
                chdir(folder)
                system(f"pdflatex -interaction=nonstopmode -file-line-error {file}")
                sleep(1)
                if not match(r".tex:[0-9]+:", open(splitext(file)[0] + ".log", "r", encoding="utf-8").read()):
                    system(f"pdflatex -interaction=nonstopmode -file-line-error {file}")
                    system(f"pdflatex -interaction=nonstopmode -file-line-error {file}")
                    if not self.debug:
                        clean_LaTeX(file)
                else:
                    warn("The LaTeX compilation terminated with an error.")
                btn_compile.setText("Compilation terminée")
            except:
                btn_compile.setText("Une erreur est survenue")
            chdir(self.file_dir)

        btn_preview.clicked.connect(preview_sheet)
        btn_compile.clicked.connect(compile_sheet)

        dialog.exec()

    def gen_exercises_with(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Compilation des feuilles d\u2019exercices")
        dialog.setStyleSheet("background-color: #121212;")
        dialog.setWindowIcon(QIcon("favicon.ico"))
        dialog.setModal(True)
        dialog.keyPressEvent = lambda a0: disable_escape(a0, dialog)
        
        layout = QVBoxLayout(dialog)
        label = QLabel("\t\t")
        label.setStyleSheet("color: white; font-size: 16px;")
        layout.addWidget(label)
        
        btn_close = QPushButton("Fermer")
        btn_close.setStyleSheet("background-color: #a30000; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        btn_close.clicked.connect(dialog.close)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(btn_close)
        
        dialog.open()
        
        flnm, _ = QFileDialog.getOpenFileName(dialog, "Sélectionner un fichier", "", "text files (*.txt)")
        if not flnm:
            flnm, _ = QFileDialog.getOpenFileName(dialog, "Sélectionner un fichier", "", "text files (*.txt)")
        if not flnm:
            dialog.close()
            return None
        filecontent = open(flnm, "r", encoding="utf-8").readline()
        sheet, extra = filecontent.split(";;;")
        students = sheet.split(";;")
        sheet_flnm = splitext(flnm)[0] + ".tex"
        all_flnm = splitext(flnm)[0] + "_all.tex"
        rapport_flnm = splitext(flnm)[0] + "_rapport.tex"

        generate_exercise_sheet(get_exercises(self.db, students[0]), get_exercises(self.db, students[1]), get_exercises(self.db, students[2]), len(str(self.db.max_exercises())), sheet_flnm)
        label.setText(f"Compilation de {basename(sheet_flnm)} en cours")
        self.app.processEvents()
        try:
            folder, file = split(sheet_flnm)
            chdir(folder)
            system(f"pdflatex -interaction=nonstopmode -file-line-error {sheet_flnm}")
            sleep(1)
            if not match(r".tex:[0-9]+:", open(splitext(file)[0] + ".log", "r", encoding="utf-8").read()):
                system(f"pdflatex -interaction=nonstopmode -file-line-error {sheet_flnm}")
                system(f"pdflatex -interaction=nonstopmode -file-line-error {sheet_flnm}")
                if not self.debug:
                    clean_LaTeX(sheet_flnm)
            else:
                warn("The LaTeX compilation terminated with an error.")
            label.setText("Compilation terminée")
        except:
            label.setText("Une erreur est survenue")
        chdir(self.file_dir)
        
        sleep(1)

        gen_exercise_book(self.db, all_flnm, filecontent, True, True, True, True, False)
        label.setText(f"Compilation de {basename(all_flnm)} en cours")
        self.app.processEvents()
        try:
            folder, file = split(all_flnm)
            chdir(folder)
            system(f"pdflatex -interaction=nonstopmode -file-line-error {all_flnm}")
            sleep(1)
            if not match(r".tex:[0-9]+:", open(splitext(file)[0] + ".log", "r", encoding="utf-8").read()):
                system(f"pdflatex -interaction=nonstopmode -file-line-error {all_flnm}")
                system(f"pdflatex -interaction=nonstopmode -file-line-error {all_flnm}")
                if not self.debug:
                    clean_LaTeX(all_flnm)
            else:
                warn("The LaTeX compilation terminated with an error.")
            label.setText("Compilation terminée")
        except:
            label.setText("Une erreur est survenue")
        chdir(self.file_dir)
        
        sleep(1)

        gen_recap(self.db, rapport_flnm, (students, extra), False, False, False, False, False)

        label.setText(f"Processus terminé\nFermeture de la fenêtre")
        self.app.processEvents()

        sleep(1)

        dialog.close()

    def gen_book(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Visualiser les exercices")
        dialog.setStyleSheet("background-color: #121212;")
        dialog.setWindowIcon(QIcon("favicon.ico"))
        dialog.setModal(True)
        dialog.keyPressEvent = lambda a0: disable_escape(a0, dialog)

        layout = QVBoxLayout(dialog)
        
        label = QLabel(f"Exercices à ajouter")
        label.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(label)

        input_field = QLineEdit()
        input_field.setPlaceholderText(f"Exercices à ajouter")
        input_field.setStyleSheet("background-color: #333; color: white; font-size: 14px; padding: 8px; border-radius: 5px;")
        input_field.setText("*")
        layout.addWidget(input_field)

        # Input: Compteur parent des exercices
        compteur_label = QLabel("Compteur parent des exercices")
        compteur_label.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(compteur_label)

        compteur_input = QLineEdit()
        compteur_input.setStyleSheet("background-color: #333; color: white; font-size: 14px; padding: 5px;")
        layout.addWidget(compteur_input)
        compteur_input.setText("subsection")

        # Checkbox: Afficher les réponses
        checkbox = QCheckBox("Afficher les réponses")
        checkbox.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(checkbox)
        checkbox.setChecked(True)

        d_checkbox = QCheckBox("Afficher la difficulté")
        d_checkbox.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(d_checkbox)
        d_checkbox.setChecked(True)

        id_checkbox = QCheckBox("Afficher l\u2019identifiant")
        id_checkbox.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(id_checkbox)
        id_checkbox.setChecked(True)

        t_checkbox = QCheckBox("Afficher les titres")
        t_checkbox.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(t_checkbox)
        t_checkbox.setChecked(True)

        r_checkbox = QCheckBox("Afficher les chapitres requis")
        r_checkbox.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(r_checkbox)
        r_checkbox.setChecked(True)

        # Destination selection
        dest_button = QPushButton("Destination")
        dest_button.setCursor(Qt.CursorShape.PointingHandCursor)
        dest_button.setMaximumWidth(350)
        dest_button.setStyleSheet("background-color: #555; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        layout.addWidget(dest_button)

        dest_path = {"path": ""}  # Mutable to capture path from inner scope

        def choose_destination():
            file_path, _ = QFileDialog.getSaveFileName(dialog, "Choisir le fichier", "", "LaTeX files (*.tex)")
            if file_path:
                dest_path["path"] = file_path
                dest_button.setText(f"Destination: {file_path}")

        dest_button.clicked.connect(choose_destination)

        # Action Buttons (Preview / Compile / Cancel)
        button_layout = QHBoxLayout()

        btn_compile = QPushButton("Compiler")
        btn_compile.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_compile.setStyleSheet("background-color: #003366; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        button_layout.addWidget(btn_compile)

        btn_cancel = QPushButton("Annuler")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("background-color: #a30000; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        btn_cancel.clicked.connect(dialog.close)
        button_layout.addWidget(btn_cancel)

        layout.addLayout(button_layout)

        def compile_book():
            exs = input_field.text()
            if exs == "*":
                gen_book(self.db, dest_path["path"], compteur_input.text(), checkbox.isChecked(), d_checkbox.isChecked())
            else:
                gen_exercise_book(self.db, dest_path["path"], exs,  checkbox.isChecked(), d_checkbox.isChecked())
            btn_compile.setText("Compilation en cours")
            self.app.processEvents()
            try:
                folder, file = split(dest_path['path'])
                chdir(folder)
                system(f"pdflatex -interaction=nonstopmode -file-line-error {file}")
                sleep(1)
                if not match(r".tex:[0-9]+:", open(splitext(file)[0] + ".log", "r", encoding="utf-8").read()):
                    system(f"pdflatex -interaction=nonstopmode -file-line-error {file}")
                    system(f"pdflatex -interaction=nonstopmode -file-line-error {file}")
                    if not self.debug:
                        clean_LaTeX(file)
                else:
                    warn("The LaTeX compilation terminated with an error.")
                btn_compile.setText("Compilation terminée")
            except:
                btn_compile.setText("Une erreur est survenue")
            chdir(self.file_dir)

        btn_compile.clicked.connect(compile_book)

        dialog.exec()

    def export_exercises(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Exporter des exercices")
        dialog.setStyleSheet("background-color: #121212;")
        dialog.setWindowIcon(QIcon("favicon.ico"))
        dialog.setModal(True)
        dialog.keyPressEvent = lambda a0: disable_escape(a0, dialog)

        layout = QVBoxLayout(dialog)

        label = QLabel(f"Exercices à exporter")
        label.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(label)

        input_field = QLineEdit()
        input_field.setPlaceholderText(f"Exercices à exporter")
        input_field.setStyleSheet("background-color: #333; color: white; font-size: 14px; padding: 8px; border-radius: 5px;")
        layout.addWidget(input_field)

        # Destination selection
        dest_button = QPushButton("Destination")
        dest_button.setCursor(Qt.CursorShape.PointingHandCursor)
        dest_button.setMaximumWidth(350)
        dest_button.setStyleSheet("background-color: #555; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        layout.addWidget(dest_button)

        dest_path = {"path": ""}  # Mutable to capture path from inner scope

        def choose_destination():
            file_path, _ = QFileDialog.getSaveFileName(dialog, "Choisir le fichier", "", "Zip files (*.zip)")
            if file_path:
                dest_path["path"] = file_path
                dest_button.setText(f"Destination: {file_path}")

        dest_button.clicked.connect(choose_destination)

        button_layout = QHBoxLayout()

        btn_exp = QPushButton("Exporter les exercices")
        btn_exp.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_exp.setStyleSheet("background-color: #336600; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        button_layout.addWidget(btn_exp)

        btn_cancel = QPushButton("Annuler")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("background-color: #a30000; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        btn_cancel.clicked.connect(dialog.close)
        button_layout.addWidget(btn_cancel)

        layout.addLayout(button_layout)

        def export_zip():
            export_ex(self.db, dest_path["path"], list(map(int, filter(lambda x: x != "", input_field.text().split(";")))))
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Exporter des exercices")
            dlg.setText("Export effectué")
            button = dlg.exec()

            dialog.accept()

        btn_exp.clicked.connect(export_zip)

        dialog.exec()

    def import_exercises(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Importer des exercices")
        dialog.setStyleSheet("background-color: #121212;")
        dialog.setWindowIcon(QIcon("favicon.ico"))
        dialog.setModal(True)
        dialog.keyPressEvent = lambda a0: disable_escape(a0, dialog)

        layout = QVBoxLayout(dialog)

        # File select button
        file_button = QPushButton("Choisir un fichier")
        file_button.setCursor(Qt.CursorShape.PointingHandCursor)
        file_button.setStyleSheet("background-color: #003366; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        layout.addWidget(file_button)

        file_path = {"path": ""}

        def choose_file():
            flnm, _ = QFileDialog.getOpenFileName(dialog, "Sélectionner un fichier", "", "zip files (*.zip)")
            if flnm:
                file_path["path"] = flnm
                file_button.setText(f"Fichier : {basename(flnm)}")

        file_button.clicked.connect(choose_file)

        # Buttons
        button_layout = QHBoxLayout()

        import_button = QPushButton("Importer")
        import_button.setCursor(Qt.CursorShape.PointingHandCursor)
        import_button.setStyleSheet("background-color: #006600; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        button_layout.addWidget(import_button)

        cancel_button = QPushButton("Annuler")
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_button.setStyleSheet("background-color: #a30000; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        cancel_button.clicked.connect(dialog.close)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        def _import():
            if file_path["path"]:
                import_ex(self, self.db, file_path["path"])
                dialog.accept()
            else:
                error_label = QLabel("Aucun fichier sélectionné.")
                error_label.setStyleSheet("color: red; font-size: 12px;")
                layout.addWidget(error_label)

        import_button.clicked.connect(_import)

        dialog.exec()

    def open_window(self, title: str = "Title", lcontent: list[str] = ["Content"]):
        # Dummy window
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setStyleSheet("background-color: #121212;")
        dialog.setWindowIcon(QIcon("favicon.ico"))
        dialog.setModal(True)
        dialog.keyPressEvent = lambda a0: disable_escape(a0, dialog)
        
        layout = QVBoxLayout(dialog)
        for content in lcontent:
            label = QLabel(content)
            label.setStyleSheet("color: white; font-size: 16px;")
            layout.addWidget(label)
        
        btn_close = QPushButton("Fermer")
        btn_close.setStyleSheet("background-color: #a30000; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        btn_close.clicked.connect(dialog.close)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(btn_close)
        
        dialog.exec()
