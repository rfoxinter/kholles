from zipfile import ZipFile, ZIP_DEFLATED

def compress(db: bytes, flnm: str = "exercices.db.zip") -> None:
    myzip = ZipFile(flnm, "w", compression=ZIP_DEFLATED, compresslevel=9)
    myzip.writestr("exercices.db", db)
    myzip.close()

def uncompress():
    myzip = ZipFile("exercices.db.zip", "r", compression=ZIP_DEFLATED, compresslevel=9)
    db = myzip.open("exercices.db", "r").read()
    return db