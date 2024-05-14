from pathlib import Path
import sys

civiltools_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(civiltools_path))

import pytest
from building.build import (
    StructureSystem,
    Building,
)
from exporter import export_to_word

import civiltools_python_functions


def test_export():
    h1 = 26.28
    h2 = 3.55
    tx_an = 1.76
    ty_an = 1.99
    x = StructureSystem("سیستم قاب خمشی", "قاب خمشی بتن آرمه متوسط", 'X')
    x2 = StructureSystem("سیستم دیوارهای باربر", "دیوارهای برشی بتن آرمه ویژه", 'X')
    building = Building("زیاد", 1, 'II', "قم", 6, h1, None, x, x, tx_an, ty_an,
                                   x2, x2, h2, False, 2)
    filename = civiltools_python_functions.get_temp_filepath(suffix='docx')
    filename = 'ali.docx'
    export_to_word.export(building, filename)
    civiltools_python_functions.open_file(filename)


def test_building():
    x = StructureSystem("سیستم قاب خمشی", "قاب خمشی بتن آرمه متوسط", 'X')
    building = Building("زیاد", 1, 'II', "قم", 8, 26.28, None, x, x, 1.76, 1.99)
