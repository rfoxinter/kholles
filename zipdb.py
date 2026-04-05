from os.path import getsize
from zipfile import ZIP_LZMA, ZipFile

from database import dbversion

def compress(db: bytes, flnm: str = "exercices.db.zip", version: int = 0) -> float:
    myzip = ZipFile(flnm, "w", compression=ZIP_LZMA, compresslevel=9)
    myzip.writestr("exercices.db", db)
    if version == 0:
        myzip.writestr("VERSION", str(dbversion))
    else:
        myzip.writestr("VERSION", str(version))
    myzip.close()
    return getsize(flnm)/len(db)

def uncompress() -> tuple[bytes, bool, int]:
    try:
        myzip = ZipFile("exercices.db.zip", "r", compression=ZIP_LZMA, compresslevel=9)
        db = myzip.open("exercices.db", "r").read()
        version = 1
        if "VERSION" in myzip.namelist():
            version = int(myzip.open("VERSION", "r").read())
        return db, True, version
    except FileNotFoundError:
        return b'', False, 0