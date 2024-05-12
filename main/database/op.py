from asgiref.sync import sync_to_async
from datetime import datetime
from typing import List
from .assigments_model.models import Activity, Matkul, Materi, NoticedDeadlineActivity, NoticedOpenTimeActivity

def _get_matkul(name):
    try:
        return Matkul.objects.get(name=name)
    except Matkul.DoesNotExist:
        return None

@sync_to_async
def get_matkul(*args, **kwargs):
    return _get_matkul(*args, **kwargs)

@sync_to_async
def create_matkul(name):
    c = _get_matkul(name=name)
    if c is None:
        c = Matkul(name=name)
        c.save()
    
    return c

def _get_materi(name, matkul):
    try:
        return Materi.objects.get(name=name, matkul=matkul)
    except Materi.DoesNotExist:
        return None

@sync_to_async
def get_materi(*args, **kwargs):
    return _get_materi(*args, **kwargs)

@sync_to_async
def create_materi(name, matkul):
    m = _get_materi(name=name, matkul=matkul)
    if m is None:
        m = Materi(name=name, matkul=matkul)
        m.save()

    return m

def _get_activity(id_num: str):
    try:
        return Activity.objects.get(id_num=id_num)
    except Activity.DoesNotExist:
        return None

@sync_to_async
def get_activity(*args, **kwargs):
    return _get_activity(*args, **kwargs)

@sync_to_async
def get_all_activities() -> List[Activity]:
    cache = []
    for item in Activity.objects.all():
        # Access all foreign objects to prevent error
        item.materi.matkul
        cache.append(item)
    
    return cache

@sync_to_async
def remove_activity(act: Activity):
    a = _get_activity(act.id_num)
    a.delete()

@sync_to_async
def create_activity(
    materi: Materi,
    name: str,
    id_num: str,
    type: str,
    url: str,
    deadline: datetime | None = None,
    open_time: datetime | None = None,
):
    a = _get_activity(id_num=id_num)
    if a is None:
        a = Activity(
            materi=materi,
            name=name,
            id_num=id_num,
            type=type,
            url=url,
            deadline=deadline,
            open_time=open_time
        )
        a.save()
    
    return a

def _check_notice_open_time_activity(act: Activity):
    try:
        n = NoticedOpenTimeActivity.objects.get(activity=act)
    except NoticedOpenTimeActivity.DoesNotExist:
        return False
    
    return n.noticed

@sync_to_async
def check_notice_open_time_activity(*args, **kwargs):
    return _check_notice_open_time_activity(*args, **kwargs)

@sync_to_async
def notice_open_time_activity(act: Activity):
    n = NoticedOpenTimeActivity(
        activity=act,
        noticed=True
    )
    n.save()

def _check_notice_deadline_activity(act: Activity):
    try:
        n = NoticedDeadlineActivity.objects.get(activity=act)
    except NoticedDeadlineActivity.DoesNotExist:
        return False
    
    return n.noticed

@sync_to_async
def check_notice_deadline_activity(*args, **kwargs):
    return _check_notice_deadline_activity(*args, **kwargs)

@sync_to_async
def notice_deadline_activity(act: Activity):
    n = NoticedDeadlineActivity(
        activity=act,
        noticed=True
    )
    n.save()