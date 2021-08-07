from pathlib import Path

test_folder = Path(__file__).parent


for f in test_folder.glob('**/*'):
    if f.suffix not in  ('.py', ''):
        if f.name in (
            'shayesteh.EDB',
            'pytest.ini',
            
        ):
            continue
        else:
            f.unlink()

