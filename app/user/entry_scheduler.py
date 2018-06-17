from datetime import datetime
from dateutil.relativedelta import relativedelta
from bson.objectid import ObjectId
from apscheduler.schedulers.base import JobLookupError

from app import scheduler
from app.home.user_loging_manager import User
from app.home.money_entry import MoneyEntry


def __remove_from_scheduler(mid: str):
    try:
        scheduler.remove_job(job_id=mid)
    except JobLookupError:
        return


def __add_to_scheduler(uid: ObjectId, entry: MoneyEntry):
    mid = str(entry.id)
    date = entry.date
    scheduler.add_job(__recurring, 'date', run_date=date, id=mid, args=[uid, mid])


def __recurring(uid: ObjectId, mid: str):
    us = User.objects(id=uid).first()
    if not us:
        return

    for entry in us.entries:
        if str(entry.id) == mid:
            if entry.state == MoneyEntry.State.PENDING:
                entry.state = MoneyEntry.State.APPROVED
                entry.save()

            __add_to_scheduler_pending_entry(us, entry)
            return


def __relativedelta_from_recurring(rec: MoneyEntry.Recurring):
    if rec == MoneyEntry.Recurring.EVERY_DAY:
        return relativedelta(days=1)
    elif rec == MoneyEntry.Recurring.EVERY_MONTH:
        return relativedelta(months=1)
    elif rec == MoneyEntry.Recurring.EVERY_YEAR:
        return relativedelta(years=1)
    else:
        return None


def __add_to_scheduler_pending_entry(us: User, entry: MoneyEntry):
    if entry.state == MoneyEntry.State.PENDING:
        __add_to_scheduler(us.id, entry)
        return

    assert (entry.state == MoneyEntry.State.APPROVED), "Entry state should be APPROVED!"
    rel = __relativedelta_from_recurring(entry.recurring)
    if not rel:
        return

    date = entry.date + rel
    if date < datetime.now():
        return

    cloned = entry.clone()
    cloned.date = date
    cloned.state = MoneyEntry.State.PENDING

    us.entries.append(cloned)
    us.save()
    __add_to_scheduler(us.id, cloned)


# public
def add_entry(us: User, entry: MoneyEntry):
    us.entries.append(entry)
    us.save()
    __add_to_scheduler_pending_entry(us, entry)


def edit_entry(us: User, entry: MoneyEntry):
    entry.save()

    # remove from scheduler
    mid = str(entry.id)
    __remove_from_scheduler(mid)

    __add_to_scheduler_pending_entry(us, entry)


def remove_entry(us: User, mid: str):
    for entry in us.entries:
        if str(entry.id) == mid:
            us.entries.remove(entry)
            us.save()
            break

        __remove_from_scheduler(mid)
