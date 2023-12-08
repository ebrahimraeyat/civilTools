import json
from json import JSONDecodeError
from typing import Union

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
		'bot_x1_combo',
		'top_x1_combo',
		'top_story_for_height1',
		'dead_combobox',
		'sdead_combobox',
		'partition_dead_combobox',
		'live_combobox',
		'lred_combobox',
		'live_parking_combobox',
		'lroof_combobox',
		'live5_combobox',
		'lred5_combobox',
		'partition_live_combobox',
		'mass_combobox',
		'ev_combobox',
		'hxp_combobox',
		'hxn_combobox',
		'hyp_combobox',
		'hyn_combobox',
		# Seismic
		'ex_combobox',
		'exp_combobox',
		'exn_combobox',
		'ey_combobox',
		'eyp_combobox',
		'eyn_combobox',
		'rhox_combobox',
		'rhoy_combobox',
		'ex1_combobox',
		'exp1_combobox',
		'exn1_combobox',
		'ey1_combobox',
		'eyp1_combobox',
		'eyn1_combobox',
		'rhox1_combobox',
		'rhoy1_combobox',
		):
		if hasattr(widget, key):
			exec(f"new_d['{key}'] = widget.{key}.currentText()")
	# Spinboxes
	for key in (
		'height_x',
		'no_of_story_x',
		'height_x1',
		'no_of_story_x1',
		't_an_x',
		't_an_y',
		't_an_x1',
		't_an_y1',
		):
		if hasattr(widget, key):
			exec(f"new_d['{key}'] = widget.{key}.value()")
	# Checkboxes
	for key in (
		'top_story_for_height_checkbox',
		'infill',
		'top_story_for_height_checkbox_1',
		'infill_1',
		'activate_second_system',
		'partition_dead_checkbox',
		# Irregularity
		'torsional_irregularity_groupbox',
		'torsion_irregular_checkbox',
		'extreme_torsion_irregular_checkbox',
		'reentrance_corner_checkbox',
		'diaphragm_discontinuity_checkbox',
		'out_of_plane_offset_checkbox',
		'nonparallel_system_checkbox',
		'stiffness_soft_story_groupbox',
		'stiffness_irregular_checkbox',
		'extreme_stiffness_irregular_checkbox',
		'weight_mass_checkbox',
		'geometric_checkbox',
		'in_plane_discontinuity_checkbox',
		'lateral_strength_weak_story_checkbox',
		# System type
		'concrete_radiobutton',
		'steel_radiobutton',
		):
		if hasattr(widget, key):
			exec(f"new_d['{key}'] = widget.{key}.isChecked()")
	from building import RuTable
	if hasattr(widget, 'x_treeview'):
		system, lateral, i, n = get_treeview_item_prop(widget.x_treeview)
		new_d['x_system'] = [i, n]
		new_d['x_system_name'] = system
		new_d['x_lateral_name'] = lateral
		new_d['cdx'] = RuTable.Ru[system][lateral][2]
	if hasattr(widget, 'y_treeview'):
		system, lateral, i, n = get_treeview_item_prop(widget.y_treeview)
		new_d['y_system'] = [i, n]
		new_d['y_system_name'] = system
		new_d['y_lateral_name'] = lateral
		new_d['cdy'] = RuTable.Ru[system][lateral][2]
	# second system
	if hasattr(widget, 'x_treeview_1'):
		system, lateral, i, n = get_treeview_item_prop(widget.x_treeview_1)
		new_d['x_system_1'] = [i, n]
		new_d['x_system_name_1'] = system
		new_d['x_lateral_name_1'] = lateral
		new_d['cdx1'] = RuTable.Ru[system][lateral][2]
	if hasattr(widget, 'y_treeview_1'):
		system, lateral, i, n = get_treeview_item_prop(widget.y_treeview_1)
		new_d['y_system_1'] = [i, n]
		new_d['y_system_name_1'] = system
		new_d['y_lateral_name_1'] = lateral
		new_d['cdy1'] = RuTable.Ru[system][lateral][2]
	d = get_settings_from_etabs(etabs)
	d.update(new_d)
	set_settings_to_etabs(etabs, d)

def update_setting(
	etabs,
	keys: Union[list, dict],
	values: Union[list, None] = None,
	):
	'''
	update etabs setting dictionary with keys and values or dict 
	'''
	d = get_settings_from_etabs(etabs)
	if isinstance(keys, dict):
		new_d = keys
	else:
		new_d = dict(zip(keys, values))
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
	
def save_analytical_periods(etabs, tx, ty, tx1=4, ty1=4):
	d = get_settings_from_etabs(etabs)
	d['t_an_x'] = tx
	d['t_an_y'] = ty
	d['t_an_x1'] = tx1
	d['t_an_y1'] = ty1
	set_settings_to_etabs(etabs, d)

def get_analytical_periods(etabs):
	d = get_settings_from_etabs(etabs)
	tx = d.get('t_an_x', 4)
	ty = d.get('t_an_y', 4)
	tx1 = d.get('t_an_x1', 4)
	ty1 = d.get('t_an_y1', 4)
	return tx, ty, tx1, ty1

def save_cd(etabs, cdx, cdy, cdx1=0, cdy1=0):
	d = get_settings_from_etabs(etabs)
	d['cdx'] = cdx
	d['cdy'] = cdy
	d['cdx1'] = cdx1
	d['cdy1'] = cdy1
	set_settings_to_etabs(etabs, d)

def get_cd(etabs):
	d = get_settings_from_etabs(etabs)
	cdx = d.get('cdx')
	cdy = d.get('cdy')
	cdx1 = d.get('cdx1', 0)
	cdy1 = d.get('cdy1', 0)
	return cdx, cdy, cdx1, cdy1

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
	# Seismic
	seismic_loads = etabs.load_patterns.get_seismic_load_patterns()
	for (e1combobox, e2combobox), names in zip((
		('ex_combobox', 'ex1_combobox'),
		('exn_combobox', 'exn1_combobox'),
		('exp_combobox', 'exp1_combobox'),
		('ey_combobox', 'ey1_combobox'),
		('eyn_combobox', 'eyn1_combobox'),
		('eyp_combobox', 'eyp1_combobox')), seismic_loads
	):
		for ecombobox in (e1combobox, e2combobox):
			if hasattr(widget, ecombobox):
				if names:
					# exec(f"all_item_text = [f'{widget.{ecombobox}.itemText('i')}' for i in range(widget.{ecombobox}.count())]")
					# exec(f"add_names = {names}.difference(all_item_text)")
					# exec("print(names, ecombobox)")
					exec(f"widget.{ecombobox}.clear()")
					exec(f"widget.{ecombobox}.addItems(names)")
				if ecombobox in keys:
					exec(f"index = widget.{ecombobox}.findText(d['{ecombobox}'])")
					exec(f"widget.{ecombobox}.setCurrentIndex(index)")
	for key in (
		'ostan',
		'city',
		'risk_level',
		'soil_type',
		'importance_factor',
		'bot_x_combo',
		'top_x_combo',
		'top_story_for_height',
		'bot_x1_combo',
		'top_x1_combo',
		'top_story_for_height1',
		# loads
		'dead_combobox',
		'sdead_combobox',
		'partition_dead_combobox',
		'live_combobox',
		'lred_combobox',
		'live_parking_combobox',
		'lroof_combobox',
		'live5_combobox',
		'lred5_combobox',
		'partition_live_combobox',
		'mass_combobox',
		'ev_combobox',
		'hxp_combobox',
		'hxn_combobox',
		'hyp_combobox',
		'hyn_combobox',
		# Rho
		'rhox_combobox',
		'rhoy_combobox',
		'rhox1_combobox',
		'rhoy1_combobox',
		):
		if key in keys and hasattr(widget, key):
			exec(f"index = widget.{key}.findText(d['{key}'])")
			exec(f"widget.{key}.setCurrentIndex(index)")
		elif key in ('ostan', 'city') and hasattr(widget, key):
			exec(f"index = widget.{key}.findText('قم')")
			exec(f"widget.{key}.setCurrentIndex(index)")
	# Set risk number
	key = 'risk_level'
	if hasattr(widget, 'acc') and key in keys:
		accs = [
				'کم',
				'متوسط',
				'زیاد',
				'خیلی زیاد',
				]
		risk_level = d[key]
		i = accs.index(risk_level)
		widget.acc.setCurrentIndex(i)

	# Checkboxes
	key = 'top_story_for_height_checkbox'
	if key in keys and hasattr(widget, key):
		checked = d.get(key, True)
		widget.top_story_for_height_checkbox.setChecked(checked)
		widget.top_story_for_height.setEnabled(checked)
	key = 'top_story_for_height_checkbox_1'
	if key in keys and hasattr(widget, key):
		checked = d.get(key, True)
		widget.top_story_for_height_checkbox_1.setChecked(checked)
		widget.top_story_for_height1.setEnabled(checked)
	for key in (
		'infill',
		'infill_1',
		# Irregularity
		'torsional_irregularity_groupbox',
		'torsion_irregular_checkbox',
		'extreme_torsion_irregular_checkbox',
		'reentrance_corner_checkbox',
		'diaphragm_discontinuity_checkbox',
		'out_of_plane_offset_checkbox',
		'nonparallel_system_checkbox',
		'stiffness_soft_story_groupbox',
		'stiffness_irregular_checkbox',
		'extreme_stiffness_irregular_checkbox',
		'weight_mass_checkbox',
		'geometric_checkbox',
		'in_plane_discontinuity_checkbox',
		'lateral_strength_weak_story_checkbox',
	):
		if key in keys and hasattr(widget, key):
			exec(f'widget.{key}.setChecked(d["{key}"])')
	# Structure type
	key = 'steel_radiobutton'
	if hasattr(widget, key) and hasattr(widget, 'concrete_radiobutton'):
		if  key in keys:
			exec(f'widget.{key}.setChecked(d["{key}"])')
		else:
			structure_type = etabs.get_type_of_structure()
			if structure_type == 'steel':
				exec(f'widget.{key}.setChecked(True)')

	key = 'partition_dead_checkbox'
	if key in keys and hasattr(widget, key):
		checked = d.get(key, False)
		widget.partition_dead_checkbox.setChecked(checked)
		widget.partition_dead_combobox.setEnabled(checked)
		widget.partition_live_checkbox.setChecked(not checked)
		widget.partition_live_combobox.setEnabled(not checked)
	key = 'activate_second_system'
	if key in keys and hasattr(widget, key):
		checked = d.get(key, False)
		widget.activate_second_system.setChecked(checked)
		for w in (
			'x_system_label',
			'y_system_label',
			'x_treeview_1',
			'y_treeview_1',
			'stories_for_apply_earthquake_groupox',
			'stories_for_height_groupox',
			'infill_1',
			'second_earthquake_properties',
			):
			if hasattr(widget, w):
				exec(f"widget.{w}.setEnabled(checked)")
		if hasattr(widget, 'top_story_for_height_checkbox') and checked:
			widget.top_story_for_height_checkbox.setChecked(False)
			widget.top_story_for_height_checkbox.setEnabled(False)
			widget.top_story_for_height.setEnabled(False)
			d['top_story_for_height_checkbox'] = False
	# Spinboxes
	for key in (
		'height_x',
		'no_of_story_x',
		'height_x1',
		'no_of_story_x1',
		't_an_x',
		't_an_y',
		't_an_x1',
		't_an_y1',
		):
		if key in keys and hasattr(widget, key):
			exec(f"widget.{key}.setValue(d['{key}'])")
	# TreeViewes
	if hasattr(widget, 'x_treeview') and hasattr(widget, 'y_treeview'):
		x_item = d.get('x_system', [2, 1])
		y_item = d.get('y_system', [2, 1])
		select_treeview_item(widget.x_treeview, *x_item)
		select_treeview_item(widget.y_treeview, *y_item)
	if hasattr(widget, 'x_treeview_1') and hasattr(widget, 'y_treeview_1'):
		x_item = d.get('x_system_1', [2, 1])
		y_item = d.get('y_system_1', [2, 1])
		select_treeview_item(widget.x_treeview_1, *x_item)
		select_treeview_item(widget.y_treeview_1, *y_item)
	return d

def select_treeview_item(view, i, n):
	root_index = view.model().index(i, 0, QtCore.QModelIndex())
	child_index = view.model().index(n, 0, root_index)
	view.clearSelection()
	view.setCurrentIndex(child_index)
	view.setExpanded(child_index, True)