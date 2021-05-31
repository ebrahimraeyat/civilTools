# from unittest import mock
import pytest
from unittest.mock import Mock
from pathlib import Path
import sys
import base64

civil_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(civil_path))

from functions import check_legal


@pytest.fixture
def checklegal():
    return check_legal.CheckLegal('drift.bin', '')

def test_initiate(checklegal):
    checklegal.initiate()
    text = checklegal.get_registered_numbers()
    assert text == (0, 0)