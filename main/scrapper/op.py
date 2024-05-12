import aiohttp
import json
import logging
import re
import itertools
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from zoneinfo import ZoneInfo

from .course import Course

log = logging.getLogger(__name__)

# Student credentials
base_dir = Path(__file__).resolve().parent.parent.parent
cred = json.loads((base_dir / "credential-user.secret.json").read_text())
username = cred["username"]
password = cred["password"]

# Session setup
ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
session = aiohttp.ClientSession()
session.headers["User-Agent"] = ua

# Constants
main_url = "https://v-class.gunadarma.ac.id/my/"
login_url = "https://v-class.gunadarma.ac.id/login/index.php"
logout_url = "https://v-class.gunadarma.ac.id/login/logout.php"
attrs_form_login = {
    "action": login_url,
    "method": "post",
}
attrs_a_logout = {
    "data-title": ["logout", "moodle"]
}
attrs_section_courses = {
    "class": [
        "block_course_list",
        "block",
        "list_block"
    ],
    "data-block": "course_list"
}
html_parser_lib = "lxml"

known_activities = {
    "resource": "Materi",
    "url": "Materi (Link external)",
    "folder": "Materi (Di dalam folder)",
    "quiz": "Kuiz",
    "assign": "Tugas",
    "forum": "Forum",
    "page": "Informasi tambahan",
}

class ServerDown(Exception):
    pass

async def get_soup():
    init_response = await session.get(login_url)
    if init_response.status > 500:
        raise ServerDown("Server is down")

    content = await init_response.text()
    soup = BeautifulSoup(content, html_parser_lib)

    return soup

async def login():
    soup = await get_soup()

    result = soup.find("form", attrs=attrs_form_login)
    if result is None:
        raise RuntimeError(f"Cannot find login form")
    
    elem = result.find("input", attrs={"name": "logintoken"})
    if elem is None:
        raise RuntimeError(f"Cannot find logintoken var in login form")

    login_token = elem.attrs["value"]
    payload = {
        "anchor": "",
        "logintoken": login_token,
        "username": username,
        "password": password
    }

    r = await session.post(
        login_url,
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data=payload
    )
    content = await r.text()
    if "Rahman Yusuf 51421218" not in content:
        raise RuntimeError(f"Login error, reason: {content}")

    r = await session.get(main_url)
    content = await r.text()
    result = re.search(r'M\.cfg\s+=\s+(.{1,});var\s+', content).group(1)
    data = json.loads(result)

    session_key = data.get("sesskey")

    if session_key is None:
        raise RuntimeError("Cannot find session key in main page")

    session.key = session_key

    print("Login succesful")

async def logout():
    r = await session.get(logout_url, params={"sesskey": session.key})

    content = await r.text()
    if "You are not logged in." not in content:
        raise RuntimeError(f"Logout failed, reason: {content}")

    print("Logged out")

async def get_session_time_remaining():
    r = await session.post(
        "https://v-class.gunadarma.ac.id/lib/ajax/service.php",
        params={"sesskey": session.key, "info": "core_session_time_remaining"},
        json=[{"args": {}, "index": 0, "methodname": "core_session_time_remaining"}]
    )
    data = await r.json()

    try:
        time_left = data[0]["data"]["timeremaining"]
    except KeyError:
        raise RuntimeError(f"Returned data is invalid, data: {data}")

    return time_left

async def iter_courses_url():
    r = await session.post(
        "https://v-class.gunadarma.ac.id/lib/ajax/service.php",
        params={"sesskey": session.key, "info": "core_course_get_enrolled_courses_by_timeline_classification"},
        json=[
            {
                "args": {
                    "classification": "all",
                    "customfieldname": "",
                    "customfieldvalue": "",
                    "limit": 0,
                    "offset": 0,
                    "sort": "fullname"
                },
                "index": 0,
                "methodname": "core_course_get_enrolled_courses_by_timeline_classification"
            }
        ]
    )
    data = await r.json()
    try:
        courses = data[0]["data"]["courses"]
    except KeyError:
        raise RuntimeError(f"Returned data is invalid, data: {data}")

    for course in courses:
        yield course["viewurl"]

async def get_materi_courses(course_url):
    r = await session.get(course_url)
    content = await r.text()
    soup = BeautifulSoup(content, html_parser_lib)
    matkul = soup.find("div", attrs={"class": ["page-header-headings"]}).find("h1").decode_contents()
    # regex_replace_matkul = r"(ATA\s+2022\/2023\s+\|\s+2-FTI\s+\|\s|ATA\s+2022\/2023\s+\|\s+2IA24\s+\|\s)"
    # matkul = re.sub(regex_replace_matkul, "", matkul)
    ul = soup.find("ul", attrs={"class": ["topics"]})

    materi = []
    for num in itertools.count(start=0):
        acts = []
        li = ul.find("li", attrs={
            "id": f"section-{num}",
            "class": ["section", "main", "clearfix"],
            "role": "region"
        })

        if li is None:
            break

        li_aria_label = li.attrs["aria-label"]
        if li_aria_label == "General":
            continue

        activities = li.find("div", attrs={"class": ["content"]})
        activities = activities.find("ul", attrs={"class": ["section", "img-text"]})
        if activities is None:
            # Belum ada tugas
            continue

        activities = activities.find_all("li", attrs={"class": ["activity"]})
        for li_activity in activities:
            name_activity = None
            url_activity = None
            type_activity = None
            id_activity = None

            # MAKE SURE WE GET THE CORRECT ACTIVITIES
            li_activity_id = li_activity.attrs.get("id")
            if li_activity_id is None or "module" not in li_activity_id:
                continue

            try:
                act = li_activity.attrs["class"][1]
                type_activity = known_activities[act]
            except KeyError:
                continue

            div_mod = li_activity.find("div")
            div_mod = div_mod.find("div")
            div_mod = div_mod.find("div", attrs={"class": []})

            # Check if it's restricted
            # If it's restricted, then do not parse it
            restricted = div_mod.find("div", attrs={"class": ["availabilityinfo", "isrestricted"]})
            if restricted:
                continue

            a_elem = div_mod.find("div", attrs={"class": ["activityinstance"]}).find("a")

            url_activity = a_elem.attrs["href"]
            name_activity = a_elem.find("span", attrs={"class": ["instancename"]})
            some_random_elem = name_activity.find("span", attrs={"class": ["accesshide"]})
            if some_random_elem is not None:
                some_random_elem.decompose()
            name_activity = name_activity.decode_contents()

            found = re.search(r"\?id=(.{1,})", url_activity)
            if not found:
                raise RuntimeError("Cannot find id activity", url_activity)
            id_activity = found.group(1)

            deadline = None
            open_time = None
            if type_activity == "Kuiz":
                # Get deadline
                r = await session.get(url_activity)
                content_activity = await r.text(errors="ignore")
                r = re.search(r"This\squiz\s\will\sclose\son\s(?P<datetime>.{1,})\.\<\/p\>", content_activity)
                if r is not None:
                    d_str = r.group("datetime")
                    deadline = datetime.strptime(d_str, "%A, %d %B %Y, %I:%M %p")

                # Get open_time
                r = re.search(r"The\squiz\swill\snot\sbe\savailable\suntil\s(?P<datetime>.{1,})\<\/p\>", content_activity)
                if r is not None:
                    d_str = r.group("datetime")
                    open_time = datetime.strptime(d_str, "%A, %d %B %Y, %I:%M %p")

                if "This quiz closed on" in content_activity:
                    # Assigments is already closed, skip it
                    continue
            elif type_activity == "Tugas":
                r = await session.get(url_activity)
                content_activity = await r.text(errors="ignore")

                soup = BeautifulSoup(content_activity, html_parser_lib)
                for elem in soup.find_all("tr"):
                    th_content = None
                    th = elem.find("th")
                    if th:
                        th_content = th.decode_contents()
                    
                    td_content = None
                    td = elem.find("td")
                    if td:
                        td_content = td.decode_contents()
                    
                    if th_content == "Due date":
                        deadline = datetime.strptime(td_content, "%A, %d %B %Y, %I:%M %p")

            data = {
                "id": id_activity,
                "name": name_activity,
                "url": url_activity,
                "type": type_activity,
                "deadline": deadline,
                "open_time": open_time
            }
            acts.append(data)
        
        materi.append({
            "materi": li_aria_label,
            "activities": acts
        })

    return Course(matkul, materi)
        
