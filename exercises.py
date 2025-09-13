from re import compile, findall, finditer, sub
from warnings import warn

from database import database_exercices

def get_exercises(db: database_exercices, exlst: str) -> list[tuple[int, str, int, str, str, str, str, str]]:
    exs = []
    for _e in exlst.split(";"):
        if compile(r"[0-9]+-[0-9]+").match(_e):
            __e = list(map(int, _e.split("-")))
            f = map(str, range(__e[0], __e[1]+1))
        else:
            f = [_e]
        for e in f:
            for (ex, tags) in findall(r"([0-9]+)(?:\[(.*)\])?", e):
                _id, name, difficulty, exercise, answer, year, req_chap, chapters = db.get_exercise(int(ex))
                if tags != "":
                    exset = set()
                    for elem in tags.split(","):
                        if compile(r"[0-9]+-[0-9]+").match(elem):
                            a, b = elem.split("-")
                            for i in range(int(a), int(b) + 1):
                                exset.add(i)
                        elif compile(r"[0-9]+").match(elem):
                            exset.add(int(elem))
                        elif elem == "nohard":
                            exercise = sub(r"\\beginhard", r"\\iffalse", exercise)
                            exercise = sub(r"\\endhard", r"\\fi", exercise)
                        else:
                            warn(f"The tag {elem} does correspond to any matched pattern.")
                    if exset.__len__() > 0:
                        reps = 0
                        for ques, match in enumerate(finditer(r"\\item[^\[a-zA-Z]", exercise), start = 1):
                            if not ques in exset:
                                exercise = exercise[:match.start() + 7 * reps] + "\\hideit\\item" + exercise[match.end() - 1 + 7 * reps:]
                                reps += 1
                exs.append((_id, name, difficulty, exercise, answer, year, req_chap, chapters))
    return exs
