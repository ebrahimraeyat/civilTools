# from unittest import mock
import pytest
from unittest.mock import Mock
from pathlib import Path
import sys

civil_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(civil_path))

from functions import check_legal


@pytest.fixture
def checklegal():
    return check_legal.CheckLegal(
        filename='drift.bin',
        gist_url='',
        dir_name='TEST',
        n=3,
        )

def remove_test_folder(checklegal):
    import shutil
    test_folder = checklegal.filename.parent
    shutil.rmtree(test_folder)

def test_initiate(checklegal):
    checklegal.initiate()
    text = checklegal.get_registered_numbers()
    remove_test_folder(checklegal)
    assert text == (0, 0)

def test_is_registered(checklegal):
    ret = checklegal.is_registered
    assert ret
    ret = checklegal.is_registered
    assert ret
    remove_test_folder(checklegal)

def test_register(checklegal):
    checklegal.register()
    a, _ = checklegal.get_registered_numbers()
    remove_test_folder(checklegal)
    assert a == 1

def test_add_using_feature(checklegal):
    checklegal.add_using_feature()
    a, b = checklegal.get_registered_numbers()
    assert a == 0
    assert b == 1
    checklegal.add_using_feature()
    a, b = checklegal.get_registered_numbers()
    assert a == 0
    assert b == 2
    remove_test_folder(checklegal)

def test_allowed_to_continue(checklegal, mocker):
    allow, text = checklegal.allowed_to_continue()
    assert allow
    assert text == ''
    
    checklegal.add_using_feature()
    allow, text = checklegal.allowed_to_continue()
    assert allow
    assert text == ''

    checklegal.add_using_feature()
    allow, text = checklegal.allowed_to_continue()
    assert allow
    assert text == ''
    
    checklegal.add_using_feature()
    allow, text = checklegal.allowed_to_continue()
    assert not allow
    assert text == 'INTERNET'

    mocker.patch(
        'functions.check_legal.internet',
        return_value=True
    )
    mocker.patch(
        'functions.check_legal.CheckLegal.serial_number',
        return_value=(False, False)
    )

    allow, text = checklegal.allowed_to_continue()
    assert not allow
    assert text == 'SERIAL'

    mocker.patch(
        'functions.check_legal.CheckLegal.serial_number',
        return_value=(True, False)
    )

    allow, text = checklegal.allowed_to_continue()
    assert allow
    assert text == 'REGISTERED'

    mocker.patch(
        'functions.check_legal.internet',
        return_value=False
    )
    allow, text = checklegal.allowed_to_continue()
    assert allow
    assert text == ''
    remove_test_folder(checklegal)

    






