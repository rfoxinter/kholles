from json import load
from mimetypes import guess_type
from os.path import basename
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import uuid4
from warnings import warn

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
        data = call_api("showpublink", {"code": file_code})
        file_info = data.get("metadata")
        assert file_info
        fileid = file_info.get("fileid")
        flnm = file_info.get("name")

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
    except:
        return False

def _upload(file_path: str) -> None:
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

    req = Request(full_url, data=body)
    req.add_header("Content-Type", content_type)
    req.add_header("Content-Length", str(len(body)))
    try:
        with urlopen(req) as response:
            upload_res = load(response)["result"] == 0
    except (HTTPError, URLError):
        warn(f"An error occurred uploading {file_path}.")
        upload_res = False

    if upload_res and file_path == "exercices.db.zip":
        params = {
            "auth": token,
            "path": "/Kholles/" + file_path
        }
        url = f"https://api.pcloud.com/getfilepublink?{urlencode(params)}"
        try:
            with urlopen(url) as response:
                data = load(response)
                if data.get("result") == 0:
                    code = data["code"]
                    with open("db_code.txt", "w", encoding="utf-8") as db_code:
                        db_code.write(code)
        except (HTTPError, URLError):
            pass

def _delete(file_path: str) -> None:
    file_path = "/Kholles/" + file_path

    with open("token.txt", "r") as f:
        token = f.read().strip()

    params = {
        "auth": token,
        "path": file_path
    }
    url = f"https://api.pcloud.com/deletefile?{urlencode(params)}"
    try:
        with urlopen(url) as response:
            return load(response)["result"] == 0
    except (HTTPError, URLError) as e:
        raise e

def upload(flnms: list[str] = ["exercices.db.zip", "Exercices.pdf", "ExercicesCorriges.pdf"]) -> None:
    for flnm in flnms:
        try:
            _delete(flnm)
        except:
            pass
        _upload(flnm)

upload()