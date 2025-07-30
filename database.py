from sqlite3 import IntegrityError, connect
from warnings import warn

import zipdb

class DatabaseWarning(Warning):
    pass

class database_exercices():
    def __init__(self) -> None:
        # self.db = connect("exercices.db")
        self.db = connect(":memory:")
        uncompress, exists = zipdb.uncompress()
        if exists:
            self.db.deserialize(uncompress)
        self.bkp = connect(":memory:")
        uncompress, exists = zipdb.uncompress()
        if exists:
            self.bkp.deserialize(uncompress)
        self.cursor = self.db.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                difficulty INTEGER NOT NULL,
                exercise TEXT NOT NULL,
                answer TEXT,
                year TEXT,
                req_chap TEXT,
                chapters TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS years (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS chapters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)

    def add_chapter(self, chap_name: str) -> None:
        try:
            self.cursor.execute("""
                INSERT INTO chapters (name) VALUES (?)
            """, (chap_name,))
            self.db.commit()
        except IntegrityError:
            warn(f"Chapter {chap_name} already exists", DatabaseWarning)

    def update_chapter(self, old_name: str, new_name: str) -> None:
        try:
            self.cursor.execute("""
                UPDATE chapters
                SET name = ?
                WHERE name = ?
            """, (new_name, old_name))
            self.db.commit()
        except IntegrityError:
            warn(f"Chapter {new_name} already exists", DatabaseWarning)

    def get_chapter_id(self, name: str) -> int:
        self.cursor.execute(f"SELECT id FROM chapters WHERE name = (?)", (name,))
        return self.cursor.fetchall()[0][0]

    def get_chapter(self, _id: int) -> str:
        self.cursor.execute("SELECT name FROM chapters WHERE id = (?)", (_id,))
        for row in self.cursor.fetchall():
            return row[0]
        warn(f"No chapter with id {_id}", DatabaseWarning)
        return ""

    def list_chapters(self) -> list[str]:
        self.cursor.execute("SELECT * FROM chapters")
        return self.cursor.fetchall()

    def list_chapter_names(self) -> list[str]:
        chaps = []
        self.cursor.execute("SELECT * FROM chapters")
        for row in self.cursor.fetchall():
            chaps.append(row[1])
        return chaps

    def add_year(self, year_name: str) -> None:
        try:
            self.cursor.execute("""
                INSERT INTO years (name) VALUES (?)
            """, (year_name,))
            self.db.commit()
        except IntegrityError:
            warn(f"Year {year_name} already exists", DatabaseWarning)

    def update_year(self, old_name: str, new_name: str) -> None:
        try:
            self.cursor.execute("""
                UPDATE years
                SET name = ?
                WHERE name = ?
            """, (new_name, old_name))
            self.db.commit()
        except IntegrityError:
            warn(f"Year {new_name} already exists", DatabaseWarning)

    def get_year_id(self, name: str) -> int:
        self.cursor.execute(f"SELECT id FROM years WHERE name = (?)", (name,))
        return self.cursor.fetchall()[0][0]

    def get_year(self, _id: int) -> str:
        self.cursor.execute("SELECT name FROM years WHERE id = (?)", (_id,))
        for row in self.cursor.fetchall():
            return row[0]
        warn(f"No year with id {_id}", DatabaseWarning)
        return ""

    def list_years(self) -> list[str]:
        self.cursor.execute("SELECT * FROM years")
        return self.cursor.fetchall()

    def list_year_names(self) -> list[str]:
        years = []
        self.cursor.execute("SELECT * FROM years")
        for row in self.cursor.fetchall():
            years.append(row[1])
        return years

    def add_exercise(self, ex_name: str, ex_diff: int, ex_exr: str, ex_cor: str, ex_year: list[int], req_chap: list[int], ex_chap: list[int]) -> None:
        self.cursor.execute("""
            INSERT INTO exercises (name, difficulty, exercise, answer, year, req_chap, chapters) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (ex_name, ex_diff, ex_exr, ex_cor, "," + ",".join(map(lambda x: str(x), ex_year)) + ",", "," + ",".join(map(lambda x: str(x), req_chap)) + ",", "," + ",".join(map(lambda x: str(x), ex_chap)) + ","))
        self.db.commit()

    def update_exercise(self, _id: int, ex_name: str, ex_diff: int, ex_exr: str, ex_cor: str, ex_year: list[int], req_chap: list[int], ex_chap: list[str]) -> None:
        self.cursor.execute("""
            UPDATE exercises
            SET (name, difficulty, exercise, answer, year, req_chap, chapters) = (?, ?, ?, ?, ?, ?, ?)
            WHERE id = ?
        """, (ex_name, ex_diff, ex_exr, ex_cor, "," + ",".join(map(lambda x: str(x), ex_year)) + ",", "," + ",".join(map(lambda x: str(x), req_chap)) + ",", "," + ",".join(map(lambda x: str(x), ex_chap)) + ",", _id))
        self.db.commit()

    def list_exercises(self, param: str = "") -> list[tuple[int, str, int, str, str, str, str, str]]:
        """List all exercises in the database"""
        exrs = []
        self.cursor.execute("SELECT * FROM exercises" + ((" WHERE " + param) if param != "" else ""))
        for row in self.cursor.fetchall():
            exrs.append(row)
        return exrs

    def get_exercise(self, _id: int = -1) -> tuple[int, str, int, str, str, str, str, str]:
        """Return the data of the exercise _id with the data (id, name, difficulty, exercise, answer, year, req_chap, chapters)"""
        self.cursor.execute("SELECT * FROM exercises WHERE id = (?)", (_id,))
        for row in self.cursor.fetchall():
            return row
        warn(f"No exercise with id {_id}", DatabaseWarning)
        return (-1, "", -1, "", "", "", "", "")

    def max_exercises(self) -> int:
        self.cursor.execute("SELECT seq FROM sqlite_sequence WHERE name = 'exercises'")
        return self.cursor.fetchall()[0][0]

# db = database_exercices()
# db.update_chapter("Approximations de fonctions", "Continuité")
# # db.add_chapter("Suites de fonctions")
# # db.add_year("MP(I)")
# # db.add_exercise("Théorème de Dini", 3, "Montrer le théorème", "Corrigé", 1, [2], [])
# print(db.list_exercises())
