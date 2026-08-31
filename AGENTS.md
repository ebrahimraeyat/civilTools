# civilTools — AI agent guide

FreeCAD workbench (a "Mod") of civil/structural engineering tools that drive CSI **ETABS** through its COM API. Targets the Iranian seismic code (Standard 2800). See [README.md](README.md) for the end-user feature overview.

This Python package runs **inside FreeCAD's embedded interpreter**, not a standalone venv. `FreeCAD`, `FreeCADGui`, and `PySide` are only importable at runtime inside FreeCAD. Do not add a normal `pip` workflow or assume those modules resolve in a plain Python environment.

## Architecture

The workbench is registered in [InitGui.py](InitGui.py) (`CivilToolsWorkbench`); toolbars/menus are built from command-ID lists defined in [civilTools_gui.py](civilTools_gui.py), which also registers every command via `Gui.addCommand('command_id', CommandClass())`.

Each feature is split across three mirrored trees by category (`define`, `assign`, `control`, `edit`, `tools`, `import_export`, `shearwall`):

| Layer | Location | Role |
|-------|----------|------|
| Command | `gui_civiltools/<category>/gui_*.py` | FreeCAD command class: `GetResources()`, `Activated()`, `IsActive()` |
| Widget | `py_widget/<category>/*.py` | `Form(QtGui.QWidget)` that loads a `.ui` file and talks to ETABS |
| UI | `widgets/<category>/*.ui` | Qt Designer files |

Other key directories: `building/` (pure-Python seismic calc classes: `Building`, `StructureSystem`, `SoilProperties`), `exporter/` (settings persistence), `freecad_obj/` (build FreeCAD objects from ETABS data), `qt_models/` (Qt table/tree models), `db/` + `filehandling/` (Iran province/city + structural-system lookup data), `section/` (steel section library).

## Conventions (follow existing patterns exactly)

- **Qt is PySide, never PyQt**: `from PySide import QtCore, QtGui`, `from PySide.QtGui import QMessageBox`. Import FreeCAD as `import FreeCADGui as Gui` / `import FreeCAD`.
- **Locate bundled files relative to `__file__`**, never with hardcoded paths. Count the directory depth: from `py_widget/<category>/file.py` the root is `Path(__file__).absolute().parent.parent.parent`; from `gui_civiltools/file.py` it is `parent.parent`.
- **Load UI files** with `self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / '<category>' / 'name.ui'))`; access widgets as `self.form.<objectName>` and wire signals in a `create_connections()` method.
- **Naming**: command files `gui_*.py`; command classes `Civil*`/`CivilTools*`; command IDs snake_case (`civiltools_load_combinations`); widget classes are named `Form`.
- **Menu/tooltip strings** are wrapped in `QtCore.QT_TRANSLATE_NOOP("civiltools", "...")` for translation.

## ETABS integration

External packages — `find_etabs`, `etabs_obj` (`EtabsModel`), `python_functions`, `freecad_funcs` — live **outside this repo** and are only present in a real install. Do not try to install or stub them.

Standard `Activated()` flow (see [gui_civiltools/define/gui_create_load_combinations.py](gui_civiltools/define/gui_create_load_combinations.py)):
1. Optional license gate: `allow, check = allowed_to_continue(...)` from `gui_civiltools.gui_check_legal`; `return` early if not allowed.
2. `etabs, filename = find_etabs.find_etabs(run=False, backup=False)`; `return` if `etabs is None`.
3. Build the widget `win = <module>.Form(etabs)` and show it with `find_etabs.show_win(win, in_mdi=False)`.

Inside a `Form`, talk to ETABS via the raw COM API `self.etabs.SapModel.<Object>.<Method>(...)` or the wrapper helpers `self.etabs.<area>.<method>()` (e.g. `self.etabs.load_patterns.get_load_patterns()`). Persist UI options as JSON in the ETABS model metadata through `exporter/civiltools_config.py` (`load`, `save`, `update_setting`, `get_settings_from_etabs`) — settings travel with the `.EDB` file, not local config.

## Tests

Pure-Python logic (mostly `building/`) is tested with `unittest` under [tests/](tests). Tests use **package-relative imports** (`from ..building.build import *`), so run them as a module from the parent of the workbench folder:

```pwsh
python -m pytest civilTools/tests/test_cfactor.py
```

GUI/ETABS code cannot be unit-tested without a running FreeCAD + ETABS session; only add tests for non-GUI calculation code.
