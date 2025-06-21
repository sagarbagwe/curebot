# calendar_api.py
from datetime import datetime, timedelta

def get_next_available_slots(count=4):
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    slots = []
    for i in range(count):
        slot = now + timedelta(days=i+1)
        slot = slot.replace(hour=9)
        slots.append(slot.strftime("%Y-%m-%d %H:%M"))
    return slots
