from datetime import date, timedelta
from typing import Optional
import config


def get_predictive_tasks(intervals: dict) -> list:
    return [name for name, info in intervals.items() if info.get("predictive", False)]


def get_health_status(task_name: str, current_km: int, last_service_km: int) -> dict:
    info = config.MAINTENANCE_INTERVALS[task_name]
    km_since = current_km - last_service_km
    km_left = info['interval'] - km_since
    pct = max(0.0, min(100.0, (km_left / info['interval']) * 100))

    if pct > 40:
        status = 'ok'
    elif pct > 15:
        status = 'warning'
    else:
        status = 'critical'

    return {
        "task": task_name,
        "interval": info['interval'],
        "km_since": km_since,
        "km_left": km_left,
        "pct_remaining": pct,
        "status": status,
    }


def estimate_due_date(km_left: int, avg_km_day: float) -> Optional[date]:
    if km_left <= 0 or avg_km_day <= 0:
        return None
    days = int(km_left / avg_km_day)
    return date.today() + timedelta(days=days)
