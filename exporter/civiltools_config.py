import json
from json import JSONDecodeError

from PySide2 import QtCore

def save(etabs, widget):
	new_d = {}
	# comboboxes
	for key in (
		'ostan',
		'city',
		'risk_level',
		'soil_type',
		'importance_factor',
		'bot_x_combo',
		'top_x_combo',
		'top_story_for_height',
		):
		if hasattr(widget, key):
			exec(f"new_d['{key}'] = widget.{key}.currentText()")
	# Spinboxes
	for key in (
		'height_x',
		'no_of_story_x',
		't_an_x',
		't_an_y',
		):
		if hasattr(widget, key):
			exec(f"new_d['{key}'] = widget.{key}.value()")
	# Checkboxes
	for key in (
		'top_story_for_height_checkbox',
		'infill',
		'activate_second_system',
		):
		if hasattr(widget, key):
			exec(f"new_d['{key}'] = widget.{key}.isChecked()")

	from building import RuTable
	system, lateral, i, n = get_treeview_item_prop(widget.x_treeview)
	new_d['x_system'] = [i, n]
	new_d['x_system_name'] = system
	new_d['x_lateral_name'] = lateral
	new_d['cdx'] = RuTable.Ru[system][lateral][2]
	system, lateral, i, n = get_treeview_item_prop(widget.y_treeview)
	new_d['y_system'] = [i, n]
	new_d['y_system_name'] = system
	new_d['y_lateral_name'] = lateral
	new_d['cdy'] = RuTable.Ru[system][lateral][2]
	# second system
	system, lateral, i, n = get_treeview_item_prop(widget.x_treeview_2)
	new_d['x_system_2'] = [i, n]
	new_d['x_system_name_2'] = system
	new_d['x_lateral_name_2'] = lateral
	new_d['cdx_2'] = RuTable.Ru[system][lateral][2]
	system, lateral, i, n = get_treeview_item_prop(widget.y_treeview_2)
	new_d['y_system_2'] = [i, n]
	new_d['y_system_name_2'] = system
	new_d['y_lateral_name_2'] = lateral
	new_d['cdy_2'] = RuTable.Ru[system][lateral][2]
	d = get_settings_from_etabs(etabs)
	d.update(new_d)
	set_settings_to_etabs(etabs, d)

def set_settings_to_etabs(etabs, d: dict):
	json_str = json.dumps(d)
	etabs.SapModel.SetProjectInfo("Company Name", json_str)
	etabs.SapModel.File.Save()

def get_treeview_item_prop(view):
	indexes = view.selectedIndexes()
	if not len(indexes):
		return
	index = indexes[0]
	if index.isValid():
		data = index.internalPointer()._data
		if len(data) == 1:
			return
		lateral = data[0]
		lateral = lateral.split('-')[1]
		lateral = lateral.lstrip(' ')
		system = index.parent().data()
		system = system.split('-')[1]
		system = system.lstrip(' ')
		if hasattr(index, 'parent'):
			i = index.parent().row()
			n = index.row()
		return system, lateral, i, n
	
def save_analytical_periods(etabs, tx, ty):
	d = get_settings_from_etabs(etabs)
	d['t_an_x'] = tx
	d['t_an_y'] = ty
	set_settings_to_etabs(etabs, d)

def get_analytical_periods(etabs):
	d = get_settings_from_etabs(etabs)
	tx = d.get('t_an_x', 4)
	ty = d.get('t_an_y', 4)
	return tx, ty

def save_cd(etabs, cdx, cdy):
	d = get_settings_from_etabs(etabs)
	d['cdx'] = cdx
	d['cdy'] = cdy
	set_settings_to_etabs(etabs, d)

def get_cd(etabs):
	d = get_settings_from_etabs(etabs)
	cdx = d.get('cdx')
	cdy = d.get('cdy')
	return cdx, cdy

def get_settings_from_etabs(etabs):
	d = {}
	info = etabs.SapModel.GetProjectInfo()
	json_str = info[2][0]
	try:
		company_name = json.loads(json_str)
	except JSONDecodeError:
		return d
	if isinstance(company_name, dict):
		d = company_name
	return d

def load(etabs, widget=None):
	d = get_settings_from_etabs(etabs)
	if widget is None:
		return d
	keys = d.keys()
	for key in (
		'ostan',
		'city',
		'risk_level',
		'soil_type',
		'importance_factor',
		'bot_x_combo',
		'top_x_combo',
		'top_story_for_height',
		):
		if key in keys and hasattr(widget, key):
			exec(f"index = widget.{key}.findText(d['{key}'])")
			exec(f"widget.{key}.setCurrentIndex(index)")
		elif key in ('ostan', 'city'):
			exec(f"index = widget.{key}.findText('قم')")
			exec(f"widget.{key}.setCurrentIndex(index)")

	# Checkboxes
	key = 'top_story_for_height_checkbox'
	if key in keys and hasattr(widget, key):
		checked = d.get(key, True)
		widget.top_story_for_height_checkbox.setChecked(checked)
		widget.top_story_for_height.setEnabled(checked)
	key = 'infill'
	if key in keys and hasattr(widget, key):
		widget.infill.setChecked(d[key])
	key = 'activate_second_system'
	if key in keys and hasattr(widget, key):
		checked = d.get(key, False)
		widget.activate_second_system.setChecked(checked)
		widget.x_system_label.setEnabled(checked)
		widget.y_system_label.setEnabled(checked)
		widget.x_treeview_2.setEnabled(checked)
		widget.y_treeview_2.setEnabled(checked)
	# Spinboxes
	for key in (
		'height_x',
		'no_of_story_x',
		't_an_x',
		't_an_y',
		):
		if key in keys and hasattr(widget, key):
			exec(f"widget.{key}.setValue(d['{key}'])")
	# TreeViewes
	if hasattr(widget, 'x_treeview') and hasattr(widget, 'y_treeview'):
		x_item = d.get('x_system', [2, 1])
		y_item = d.get('y_system', [2, 1])
		select_treeview_item(widget.x_treeview, *x_item)
		select_treeview_item(widget.y_treeview, *y_item)
	if hasattr(widget, 'x_treeview_2') and hasattr(widget, 'y_treeview_2'):
		x_item = d.get('x_system_2', [2, 1])
		y_item = d.get('y_system_2', [2, 1])
		select_treeview_item(widget.x_treeview_2, *x_item)
		select_treeview_item(widget.y_treeview_2, *y_item)
	return d

def select_treeview_item(view, i, n):
	root_index = view.model().index(i, 0, QtCore.QModelIndex())
	child_index = view.model().index(n, 0, root_index)
	view.clearSelection()
	view.setCurrentIndex(child_index)
	view.setExpanded(child_index, True)