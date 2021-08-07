from pathlib import Path

civil_path = Path(__file__).parent

test_folder = civil_path / 'test'

for f in test_folder.glob('**/*'):
    if f.suffix not in  ('.py', ''):
        if f.name in (
            'shayesteh.EDB',
            'pytest.ini',
            
        ):
            continue
        else:
            f.unlink()

