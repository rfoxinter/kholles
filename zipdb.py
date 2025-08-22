from os.path import getsize
from zipfile import ZIP_LZMA, ZipFile

def compress(db: bytes, flnm: str = "exercices.db.zip") -> float:
    myzip = ZipFile(flnm, "w", compression=ZIP_LZMA, compresslevel=9)
    myzip.writestr("exercices.db", db)
    myzip.close()
    return getsize(flnm)/len(db)

def uncompress() -> tuple[bytes, bool]:
    try:
        myzip = ZipFile("exercices.db.zip", "r", compression=ZIP_LZMA, compresslevel=9)
        db = myzip.open("exercices.db", "r").read()
        return db, True
    except FileNotFoundError:
        return b'', False