import datetime

from modules.fadn import fadn


def test_set_date():
    test_instance = fadn.Fadn()
    test_instance2 = fadn.Fadn()
    test_instance3 = fadn.Fadn()
    test_instance.folder = 'fadn20250101'
    test_instance2.folder = 'xuy20101128'
    test_instance3.folder = 'randomfoldername'
    test_instance.set_date()
    test_instance2.set_date()
    test_instance3.set_date()
    assert test_instance.year == 2025
    assert test_instance.month == 1
    assert test_instance.day == 1
    assert test_instance2.year == 2010
    assert test_instance2.month == 11
    assert test_instance2.day == 28
    assert test_instance3.day == datetime.datetime.now().day
    assert test_instance3.month == datetime.datetime.now().month
    assert test_instance3.year == datetime.datetime.now().year
