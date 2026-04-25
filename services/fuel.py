import config


def categorize_service(task: str) -> str:
    task_lower = task.lower()
    if any(kw in task_lower for kw in config.COST_CATEGORY_KEYWORDS):
        return "Parts"
    return "Service"
