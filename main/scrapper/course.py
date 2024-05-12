from datetime import datetime
from typing import List

class Activity:
    def __init__(self, data):
        self._data = data
        self.id: str = data["id"]
        self.type: str = data["type"]
        self.name: str = data["name"]
        self.url: str = data["url"]
        self.deadline: datetime = data["deadline"]
        self.open_time: datetime = data["open_time"]

class Materi:
    def __init__(self, data) -> None:
        self._data = data
        self.name: str = data["materi"]
        self.activities: List[Activity] = [Activity(i) for i in data["activities"]]

class Course:
    def __init__(self, matkul, materi_data):
        self.matkul: str = matkul
        self.materi: List[Materi] = [Materi(i) for i in materi_data]
