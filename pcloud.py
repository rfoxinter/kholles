from argparse import ArgumentParser
from json import load
from mimetypes import guess_type
from os import rename
from os.path import basename, exists
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import uuid4
from warnings import warn

p = ArgumentParser()
p.add_argument('--d', help = '[d]ownload files')
p.add_argument('--u', type = str, help = '[u]pload files')
args = p.parse_args()

def call_api(endpoint, params) -> dict:
    url = f"https://api.pcloud.com/{endpoint}?{urlencode(params)}"
    with urlopen(url) as resp:
        data = load(resp)
    return data

def download() -> bool:
    try:
        file_code = open("db_code.txt", "r", encoding="utf-8").readline().strip()
    except OSError:
        print("Database not downloaded.")
        return False
    try:
        if exists("exercices.db.zip"):
            rename("exercices.db.zip", "exercices_bkp.db.zip")
    except OSError:
        print("Cannot write to exercices.db.zip.")
        return False
    data = call_api("showpublink", {"code": file_code})
    folder_info = data.get("metadata")
    assert type(folder_info) == dict
    files = folder_info.get("contents")
    assert type(files) == list
    flnm = "exercices.db.zip"
    for file in files:
        assert type(file) == dict
        if file.get("name"):
            fileid = file.get("fileid")
            break

    dl = call_api("getpublinkdownload", {"code": file_code, "fileid": fileid})
    hosts = dl.get("hosts")
    assert hosts
    path = dl.get("path")

    download_url = f"https://{hosts[0]}{path}"

    with urlopen(download_url) as resp, open(flnm, "wb") as out:
        while True:
            chunk = resp.read(8192)
            if not chunk:
                break
            out.write(chunk)

    return True

def _upload(file_path: str) -> bool:
    remote_path = "/Kholles"

    with open("token.txt", "r") as f:
        token = f.readline().strip()

    upload_url = "https://api.pcloud.com/uploadfile"
    params = {
        "auth": token,
        "path": remote_path
    }
    query_string = urlencode(params)
    full_url = f"{upload_url}?{query_string}"

    boundary = uuid4().hex
    content_type = f"multipart/form-data; boundary={boundary}"
    filename = basename(file_path)
    mime_type = guess_type(filename)[0] or "application/octet-stream"
    with open(file_path, "rb") as f:
        file_data = f.read()
    body_lines = [
        f"--{boundary}",
        f'Content-Disposition: form-data; name="file"; filename="{filename}"',
        f"Content-Type: {mime_type}",
        "",
        file_data,
        f"--{boundary}--",
        ""
    ]
    body = b"\r\n".join(
        line if isinstance(line, bytes) else line.encode("utf-8")
        for line in body_lines
    )

    req = Request(full_url, body)
    req.add_header("Content-Type", content_type)
    req.add_header("Content-Length", str(len(body)))
    try:
        with urlopen(req) as response:
            upload_res = load(response)["result"] == 0
    except (HTTPError, URLError) as e:
        warn(f"An error occurred uploading {file_path}.")
        upload_res = False

    if upload_res and file_path == "exercices.db.zip":
        params = {
            "auth": token,
            "path": "/Kholles/" + file_path
        }
        try:
            data = call_api("getfilepublink", params)
            if data.get("result") == 0:
                return True
        except (HTTPError, URLError):
            pass
    return upload_res

def _delete(file_path: str) -> None:
    file_path = "/Kholles/" + file_path

    with open("token.txt", "r") as f:
        token = f.read().strip()

    params = {
        "auth": token,
        "path": file_path
    }
    try:
        data = call_api("deletefile", params)
        return data["result"] == 0
    except (HTTPError, URLError) as e:
        raise e

def upload(flnms: list[str] = ["exercices.db.zip", "Exercices.pdf", "ExercicesCorriges.pdf"]) -> bool:
    res = True
    for flnm in flnms:
        try:
            _delete(flnm)
        except:
            pass
        res &= _upload(flnm)
    return res

if __name__ == "__main__":
    action = ""
    if (not args.d) and (not args.u):
        action = input("Choose an options [u]pload/[d]ownload: ")
    if action == "d" or args.d:
        print("Downloading database...")
        res = download()
        if not res:
            print("Downloading failed, retrying in 5 seconds.")
            sleep(5)
            print("Downloading database...")
            download()
        print("Database downloaded.")
    elif args.u:
        files = args.u.split(",")
        if files == []:
            files.append("exercices.db.zip")
        for file in files:
            fl = file.strip()
            print(f"Uploading {fl}")
            res = upload([fl])
            print(f"{fl} uploaded." if res else f"Error uploading {fl}")
    elif action == "u":
        files = input("Files to download (default: exercices.db.zip): ").split(',')
        for file in files:
            fl = file.strip()
            print(f"Uploading {fl}")
            res = upload([fl])
            print(f"{fl} uploaded." if res else f"Error uploading {fl}")
    else:
        print("Incorrect input.")