import datetime as dt


def year(request):
    """
    Добавляет переменную с текущим годом.
    """
    year1 = dt.datetime.now().year
    return {
        'year': year1
    }
