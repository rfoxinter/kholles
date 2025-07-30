from os import chdir, system
from os.path import dirname
from re import sub

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
from latex import gen_book, generate_exercise_sheet
from monokaipp import MonokaiPlusPlusStyle
from pdf_viewer import ViewerDialog



class ExerciseManager(QWidget):
    def __init__(self, app: QApplication, db: database_exercices, file_dir: str):
        super().__init__()
        self.db = db
        self.app = app
        self.file_dir = file_dir
        QFontDatabase.addApplicationFont('fonts/stars.ttf')
        QFontDatabase.addApplicationFont('fonts/Ubuntu-Regular.ttf')
        QFontDatabase.addApplicationFont('fonts/UbuntuMono-Regular.ttf')
        QFontDatabase.addApplicationFont('fonts/UbuntuMono-Bold.ttf')
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Exercise Manager")
        self.setGeometry(100, 100, 350, 350)
        self.setStyleSheet("font-family: 'Ubuntu'; font-size: 12px; background-color: #0d0d0d;")
        self.setWindowIcon(QIcon("favicon.ico"))
        
        layout = QVBoxLayout()
        buttons = [
            ("Ajouter un exercice", lambda: self.open_add_exercise_window(lambda _, b, c, d, e, f, g, h: self.db.add_exercise(b, c, d, e, f, g, h))),
            ("Modifier un exercice", self.open_edit_exercise_window),
            ("Edit Years", self.open_window),
            ("Edit Chapters", self.open_window),
            ("Générer une feuille d\u2019exercices", self.gen_exercises),
            ("Visualiser les exercices", self.gen_book)
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

    def open_add_exercise_window(self, add_func, _id: int = -1, ex_name: str = "", ex_diff: int = 6, ex_exr: str = "", ex_ans: str = "", ex_year: list = [], ex_chap: list[int] = [], ex_req_chap: list[int] = []):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter un exercice")
        # dialog.setGeometry(150, 150, 400, 500)
        dialog.setStyleSheet("font-family: 'Ubuntu'; font-size: 12px;  background-color: #121212;")
        dialog.setWindowIcon(QIcon("favicon.ico"))
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        # Title
        # title_label = QLabel("Nom de l\u2019exercice")
        # title_label.setStyleSheet("color: white; font-size: 14px;")
        # layout.addWidget(title_label)
        
        title_input = QPlainTextEdit()
        title_input.setPlainText(ex_name)
        title_input.setFixedHeight(30)
        title_input.setStyleSheet("background-color: #333; color: white; font-size: 14px;")
        title_input.setPlaceholderText('Nom de l\u2019exercice')
        layout.addWidget(title_input)
        
        # Difficulty
            # difficulty_label = QLabel("Difficulty (0-6):")
            # difficulty_label.setStyleSheet("color: white; font-size: 14px;")
            # layout.addWidget(difficulty_label)
        
        # difficulty_selector = QComboBox()
        # difficulty_selector.addItems(['B','D','E','F','G','H'])
        # difficulty_selector.setCurrentIndex(ex_diff or 0)
        # difficulty_selector.setStyleSheet("font-family: dsrom12; background-color: #333; color: white; font-size: 25px;")
        # layout.addWidget(difficulty_selector)
        difficulty_selector = QComboBox()
        labels = ['B.', 'D.', 'E.', 'F.', 'G.', 'H.', 'B', 'D', 'E', 'F', 'G', 'H']
        model = QStandardItemModel()
        for i, label in enumerate(labels):
            item = QStandardItem(label)
            if i < 6:
                item.setForeground(Qt.GlobalColor.cyan)
            else:
                item.setForeground(Qt.GlobalColor.white)
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
            for option in sorted(options):  # Ensure initial sorting
                item = QListWidgetItem(option)
                year_list_unselected.addItem(item)

        def move_year_to_selected(item):
            """Move item from unselected to selected list and keep sorting"""
            year_list_unselected.takeItem(year_list_unselected.row(item))
            year_list_selected.addItem(item)
            year_list_selected.sortItems()  # Keep sorted
            year_list_unselected.clearSelection()

        def move_year_to_unselected(item):
            """Move item from selected to unselected list and keep sorting"""
            year_list_selected.takeItem(year_list_selected.row(item))
            year_list_unselected.addItem(item)
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
            for option in sorted(options):  # Ensure initial sorting
                item = QListWidgetItem(option)
                chap_list_unselected.addItem(item)

        def move_chap_to_selected(item):
            """Move item from unselected to selected list and keep sorting"""
            chap_list_unselected.takeItem(chap_list_unselected.row(item))
            chap_list_selected.addItem(item)
            chap_list_selected.sortItems()  # Keep sorted
            chap_list_unselected.clearSelection()

        def move_chap_to_unselected(item):
            """Move item from selected to unselected list and keep sorting"""
            chap_list_selected.takeItem(chap_list_selected.row(item))
            chap_list_unselected.addItem(item)
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
            for option in sorted(options):  # Ensure initial sorting
                item = QListWidgetItem(option)
                req_chap_list_unselected.addItem(item)

        def move_req_chap_to_selected(item):
            """Move item from unselected to selected list and keep sorting"""
            req_chap_list_unselected.takeItem(req_chap_list_unselected.row(item))
            req_chap_list_selected.addItem(item)
            req_chap_list_selected.sortItems()  # Keep sorted
            req_chap_list_unselected.clearSelection()

        def move_req_chap_to_unselected(item):
            """Move item from selected to unselected list and keep sorting"""
            req_chap_list_selected.takeItem(req_chap_list_selected.row(item))
            req_chap_list_unselected.addItem(item)
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
            dlg.setText("Ajout/modification effectuée")
            button = dlg.exec()

            dialog.accept()
            # self.db.add_exercise(title_input.toPlainText(), diff, exercise_input.toPlainText(), answer_input.toPlainText(), years[0], req_chaps, chaps)

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

        layout = QVBoxLayout(dialog)

        # Integer Selector
        exercise_selector = QSpinBox()
        exercise_selector.setMinimumHeight(25)
        exercise_selector.setMinimumWidth(250)
        exercise_selector.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        exercise_selector.setMinimum(1)
        exercise_selector.setMaximum(self.db.max_exercises())
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

    def gen_exercises(self):
        dialog = QDialog(self)
        dialog.setGeometry(150, 150, 350, 250)
        dialog.setWindowTitle("Générer une feuille d’exercices")
        dialog.setStyleSheet("background-color: #121212;")
        dialog.setWindowIcon(QIcon("favicon.ico"))
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

        spinboxes = []

        # Candidate exercise inputs
        text_inputs = []

        for i in range(1, 4):
            label = QLabel(f"Exercices de l\u2019élève {i}")
            label.setStyleSheet("color: white; font-size: 14px;")
            layout.addWidget(label)

            input_field = QLineEdit()
            input_field.setPlaceholderText(f"Exercices de l\u2019élève {i}")
            input_field.setStyleSheet("background-color: #333; color: white; font-size: 14px; padding: 8px; border-radius: 5px;")
            spinboxes.append(input_field)
            layout.addWidget(input_field)

            text_inputs.append(input_field)



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
            generate_exercise_sheet(get_exercises(self.db, spinboxes[0].text()), map(lambda x: self.db.get_exercise(x), filter(lambda x: x != "", spinboxes[1].text().split(","))), map(lambda x: self.db.get_exercise(x), filter(lambda x: x != "", spinboxes[2].text().split(","))), len(str(self.db.max_exercises())), dest_path["path"], True)
            btn_preview.setText("Compilation en cours")
            try:
                system(f"pdflatex {dest_path['path']}")
                chdir(dirname(self.file_dir))
                system(f"copy \"{sub("/", "\\\\", dest_path['path']).replace(".tex", ".pdf")}\" file.pdf")
                btn_preview.setText("Prévisualiser la feuille")
                ViewerDialog(self, "file.pdf")
            except:
                btn_preview.setText("Une erreur est survenue")
                

        def compile_sheet():
            generate_exercise_sheet(get_exercises(self.db, spinboxes[0].text()), map(lambda x: self.db.get_exercise(x), filter(lambda x: x != "", spinboxes[1].text().split(","))), map(lambda x: self.db.get_exercise(x), filter(lambda x: x != "", spinboxes[2].text().split(","))), len(str(self.db.max_exercises())), dest_path["path"])
            btn_compile.setText("Compilation en cours")
            self.app.processEvents()
            try:
                system(f"pdflatex {dest_path['path']}")
                system(f"pdflatex {dest_path['path']}")
                system(f"pdflatex {dest_path['path']}")
                btn_compile.setText("Compilation terminée")
            except:
                btn_compile.setText("Une erreur est survenue")

        btn_preview.clicked.connect(preview_sheet)
        btn_compile.clicked.connect(compile_sheet)

        dialog.exec()

    # def gen_book(self):
    #     dialog = QDialog(self)
    #     dialog.setGeometry(150, 150, 350, 250)
    #     dialog.setWindowTitle("Visualiser les exercices")
    #     dialog.setStyleSheet("background-color: #121212;")
    #     dialog.setWindowIcon(QIcon("favicon.ico"))
    #     dialog.setModal(True)

    #     layout = QVBoxLayout(dialog)

    #     # Destination selection
    #     dest_button = QPushButton("Destination")
    #     dest_button.setCursor(Qt.CursorShape.PointingHandCursor)
    #     dest_button.setMaximumWidth(350)
    #     dest_button.setStyleSheet("background-color: #555; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
    #     layout.addWidget(dest_button)

    #     dest_path = {"path": ""}  # Mutable to capture path from inner scope

    #     def choose_destination():
    #         file_path, _ = QFileDialog.getSaveFileName(dialog, "Choisir le fichier", "", "LaTeX files (*.tex)")
    #         if file_path:
    #             dest_path["path"] = file_path
    #             dest_button.setText(f"Destination: {file_path}")

    #     dest_button.clicked.connect(choose_destination)

    #     # Action Buttons (Preview / Compile / Cancel)
    #     button_layout = QHBoxLayout()

    #     btn_compile = QPushButton("Compiler")
    #     btn_compile.setCursor(Qt.CursorShape.PointingHandCursor)
    #     btn_compile.setStyleSheet("background-color: #003366; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
    #     button_layout.addWidget(btn_compile)

    #     btn_cancel = QPushButton("Annuler")
    #     btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
    #     btn_cancel.setStyleSheet("background-color: #a30000; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
    #     btn_cancel.clicked.connect(dialog.close)
    #     button_layout.addWidget(btn_cancel)

    #     layout.addLayout(button_layout)

    #     def compile_book():
    #         gen_book(self.db, dest_path["path"])
    #         btn_compile.setText("Compilation en cours")
    #         try:
    #             system(f"pdflatex {dest_path['path']}")
    #             system(f"pdflatex {dest_path['path']}")
    #             system(f"pdflatex {dest_path['path']}")
    #             btn_compile.setText("Compilation terminée")
    #         except:
    #             btn_compile.setText("Une erreur est survenue")

    #     btn_compile.clicked.connect(compile_book)

    #     dialog.exec()
    def gen_book(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Visualiser les exercices")
        dialog.setStyleSheet("background-color: #121212;")
        dialog.setWindowIcon(QIcon("favicon.ico"))
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

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
            gen_book(self.db, dest_path["path"], compteur_input.text(), checkbox.isChecked())
            btn_compile.setText("Compilation en cours")
            self.app.processEvents()
            try:
                system(f"pdflatex {dest_path['path']}")
                system(f"pdflatex {dest_path['path']}")
                system(f"pdflatex {dest_path['path']}")
                btn_compile.setText("Compilation terminée")
            except:
                btn_compile.setText("Une erreur est survenue")

        btn_compile.clicked.connect(compile_book)

        dialog.exec()


    def open_window(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('title')
        dialog.setGeometry(150, 150, 350, 250)
        dialog.setStyleSheet("background-color: #121212;")
        dialog.setWindowIcon(QIcon("favicon.ico"))
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        label = QLabel('title')
        label.setStyleSheet("color: white; font-size: 16px;")
        layout.addWidget(label)
        
        btn_close = QPushButton("Close")
        btn_close.setStyleSheet("background-color: #a30000; color: white; font-size: 14px; padding: 10px; border-radius: 10px;")
        btn_close.clicked.connect(dialog.close)
        layout.addWidget(btn_close)
        
        dialog.exec()
