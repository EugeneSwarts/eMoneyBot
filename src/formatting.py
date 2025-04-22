from datetime import datetime

def format_datetime(datetime_str: str) -> str:
    """
    Форматирует строку с датой и временем.
    Преобразует ISO формат в читаемый формат даты и времени.
    
    Args:
        datetime_str (str): Строка с датой и временем в формате ISO
        
    Returns:
        str: Отформатированная дата и время в формате "дд.мм.гггг чч:мм"
    """
    return datetime.fromisoformat(datetime_str).strftime("%d.%m.%Y %H:%M") 