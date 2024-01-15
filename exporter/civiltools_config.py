import json
from typing import Union
from pathlib import Path
import csv

from PySide2 import QtCore
from PySide2.QtCore import Qt

from qt_models import treeview_system

civiltools_path = Path(__file__).absolute().parent.parent

from building.build import StructureSystem, Building
# from building import spectral
# from models import StructureModel
# from exporter import civiltools_config
from db import ostanha

def get_prop_from_widget(etabs, widget):
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
		# Dynamic Seismic
		'sx_combobox',
		'sxe_combobox',
		'sy_combobox',
		'sye_combobox',
		# Seismic Drifts
		'ex_drift_combobox',
		'exp_drift_combobox',
		'exn_drift_combobox',
		'ey_drift_combobox',
		'eyp_drift_combobox',
		'eyn_drift_combobox',
		'rhox_drift_combobox',
		'rhoy_drift_combobox',
		'ex1_drift_combobox',
		'exp1_drift_combobox',
		'exn1_drift_combobox',
		'ey1_drift_combobox',
		'eyp1_drift_combobox',
		'eyn1_drift_combobox',
		'rhox1_drift_combobox',
		'rhoy1_drift_combobox',
		# Dynamic Seismic Drifts
		'sx_drift_combobox',
		'sxe_drift_combobox',
		'sy_drift_combobox',
		'sye_drift_combobox',
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
		# new version
		'tx_an',
		'ty_an',
		'tx1_an',
		'ty1_an',
		'tx_all_an',
		'ty_all_an',
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
		'special_case',
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
		new_d['Rux'] = RuTable.Ru[system][lateral][0]
	if hasattr(widget, 'y_treeview'):
		system, lateral, i, n = get_treeview_item_prop(widget.y_treeview)
		new_d['y_system'] = [i, n]
		new_d['y_system_name'] = system
		new_d['y_lateral_name'] = lateral
		new_d['cdy'] = RuTable.Ru[system][lateral][2]
		new_d['Ruy'] = RuTable.Ru[system][lateral][0]
	# second system
	if hasattr(widget, 'x_treeview_1'):
		system, lateral, i, n = get_treeview_item_prop(widget.x_treeview_1)
		new_d['x_system_1'] = [i, n]
		new_d['x_system_name_1'] = system
		new_d['x_lateral_name_1'] = lateral
		new_d['cdx1'] = RuTable.Ru[system][lateral][2]
		new_d['Rux1'] = RuTable.Ru[system][lateral][0]
	if hasattr(widget, 'y_treeview_1'):
		system, lateral, i, n = get_treeview_item_prop(widget.y_treeview_1)
		new_d['y_system_1'] = [i, n]
		new_d['y_system_name_1'] = system
		new_d['y_lateral_name_1'] = lateral
		new_d['cdy1'] = RuTable.Ru[system][lateral][2]
		new_d['Ruy1'] = RuTable.Ru[system][lateral][0]
	d = get_settings_from_etabs(etabs)
	d.update(new_d)
	return d

def save(etabs, widget):
	d = get_prop_from_widget(etabs=etabs, widget=widget)
	set_settings_to_etabs(etabs, d)
	return d

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
	# d['t_an_x'] = tx
	# d['t_an_y'] = ty
	# d['t_an_x1'] = tx1
	# d['t_an_y1'] = ty1
	d['tx_an'] = tx
	d['ty_an'] = ty
	d['tx1_an'] = tx1
	d['ty1_an'] = ty1
	set_settings_to_etabs(etabs, d)

def get_analytical_periods(etabs):
	d = get_settings_from_etabs(etabs)
	tx = d.get('t_an_x', d.get('tx_an', 4))
	ty = d.get('t_an_y', d.get('ty_an', 4))
	tx1 = d.get('t_an_x1', d.get('tx1_an', 4))
	ty1 = d.get('t_an_y1', d.get('ty1_an', 4))
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
	except json.JSONDecodeError:
		return d
	if isinstance(company_name, dict):
		d = company_name
	return d

def load(
		etabs,
		widget=None,
		d=None,
		):
	if d is None:
		d = get_settings_from_etabs(etabs)
	if widget is None:
		return d
	fill_cities(widget)
	fill_height_and_no_of_stories(etabs, widget)
	fill_top_bot_stories(etabs, widget)
	keys = d.keys()
	# Static Seismic combobox
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
				if d.get(ecombobox, None):
					names.add(d[ecombobox])
				if names:
					exec(f"widget.{ecombobox}.clear()")
					exec(f"widget.{ecombobox}.addItems(names)")
				if ecombobox in keys:
					exec(f"index = widget.{ecombobox}.findText(d['{ecombobox}'])")
					exec(f"if index != -1: widget.{ecombobox}.setCurrentIndex(index)")
	# Static Seismic list
	if hasattr(widget, 'x_loadcase_list') and hasattr(widget, 'y_loadcase_list'):
		ex, exn, exp, ey, eyn, eyp = etabs.get_first_system_seismic(d)
		x_loadcase = [ex, exn, exp]
		y_loadcase = [ey, eyn, eyp]
		if d.get('activate_second_system', False):
			ex1, exn1, exp1, ey1, eyn1, eyp1 = etabs.get_second_system_seismic(d)
			x_loadcase.extend([ex1, exn1, exp1])
			y_loadcase.extend([ey1, eyn1, eyp1])
		widget.x_loadcase_list.addItems(x_loadcase)
		widget.y_loadcase_list.addItems(y_loadcase)
		for lw in (widget.x_loadcase_list, widget.y_loadcase_list):
			for i in range(lw.count()):
				item = lw.item(i)
				item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
				item.setCheckState(Qt.Checked)
	# Static Seismic drift list
	if hasattr(widget, 'x_drift_loadcase_list') and hasattr(widget, 'y_drift_loadcase_list'):
		ex, exn, exp, ey, eyn, eyp = etabs.get_first_system_seismic_drift(d)
		x_loadcase = [ex, exn, exp]
		y_loadcase = [ey, eyn, eyp]
		if d.get('activate_second_system', False):
			ex1, exn1, exp1, ey1, eyn1, eyp1 = etabs.get_second_system_seismic_drift(d)
			x_loadcase.extend([ex1, exn1, exp1])
			y_loadcase.extend([ey1, eyn1, eyp1])
		widget.x_drift_loadcase_list.addItems(x_loadcase)
		widget.y_drift_loadcase_list.addItems(y_loadcase)
		for lw in (widget.x_drift_loadcase_list, widget.y_drift_loadcase_list):
			for i in range(lw.count()):
				item = lw.item(i)
				item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
				item.setCheckState(Qt.Checked)
	# Dynamic Seismic
	sx, sxe, sy, sye = etabs.load_cases.get_response_spectrum_sxye_loadcases_names()
	sx_drift = {i for i in sx if 'drift' in i.lower()}
	sxe_drift = {i for i in sxe if 'drift' in i.lower()}
	sy_drift = {i for i in sy if 'drift' in i.lower()}
	sye_drift = {i for i in sye if 'drift' in i.lower()}
	sx = sx.difference(sx_drift)
	sxe = sxe.difference(sxe_drift)
	sy = sy.difference(sy_drift)
	sye = sye.difference(sye_drift)
	for combobox, spectrum_lc in zip(
		(
			'sx_combobox',
			'sxe_combobox',
			'sy_combobox',
			'sye_combobox',
			'sx_drift_combobox',
			'sxe_drift_combobox',
			'sy_drift_combobox',
			'sye_drift_combobox',
			), (sx, sxe, sy, sye, sx_drift, sxe_drift, sy_drift, sye_drift)
			):
		if hasattr(widget, combobox):
			if d.get(combobox, None):
				spectrum_lc.add(d[combobox])
			if spectrum_lc:
				exec(f"widget.{combobox}.clear()")
				exec(f"widget.{combobox}.addItems(spectrum_lc)")
			if combobox in keys:
				exec(f"index = widget.{combobox}.findText(d['{combobox}'])")
				exec(f"if index != -1: widget.{combobox}.setCurrentIndex(index)")
	# dynamic seismic loadcase list
	if hasattr(widget, 'x_dynamic_loadcase_list') and hasattr(widget, 'y_dynamic_loadcase_list'):
		sx, sxe, sy, sye = etabs.get_dynamic_loadcases(d)
		widget.x_dynamic_loadcase_list.addItems((sx, sxe))
		widget.y_dynamic_loadcase_list.addItems((sy, sye))
		for lw in (widget.x_dynamic_loadcase_list, widget.y_dynamic_loadcase_list):
			for i in range(lw.count()):
				item = lw.item(i)
				item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
				item.setCheckState(Qt.Checked)
	# dynamic seismic loadcase drift list
	if hasattr(widget, 'x_dynamic_drift_loadcase_list') and hasattr(widget, 'y_dynamic_drift_loadcase_list'):
		sx, sxe, sy, sye = etabs.get_dynamic_drift_loadcases(d)
		widget.x_dynamic_drift_loadcase_list.addItems((sx, sxe))
		widget.y_dynamic_drift_loadcase_list.addItems((sy, sye))
		for lw in (widget.x_dynamic_drift_loadcase_list, widget.y_dynamic_drift_loadcase_list):
			for i in range(lw.count()):
				item = lw.item(i)
				item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
				item.setCheckState(Qt.Checked)
	# Seismic Drifts
	seismic_loads = etabs.load_patterns.get_seismic_load_patterns(drifts=True)
	for (e1combobox, e2combobox), names in zip((
		('ex_drift_combobox', 'ex1_drift_combobox'),
		('exn_drift_combobox', 'exn1_drift_combobox'),
		('exp_drift_combobox', 'exp1_drift_combobox'),
		('ey_drift_combobox', 'ey1_drift_combobox'),
		('eyn_drift_combobox', 'eyn1_drift_combobox'),
		('eyp_drift_combobox', 'eyp1_drift_combobox')), seismic_loads
	):
		for ecombobox in (e1combobox, e2combobox):
			if hasattr(widget, ecombobox):
				if d.get(ecombobox, None):
					names.add(d[ecombobox])
				if names:
					# exec(f"all_item_text = [f'{widget.{ecombobox}.itemText('i')}' for i in range(widget.{ecombobox}.count())]")
					# exec(f"add_names = {names}.difference(all_item_text)")
					# exec("print(names, ecombobox)")
					exec(f"widget.{ecombobox}.clear()")
					exec(f"widget.{ecombobox}.addItems(names)")
				if ecombobox in keys:
					exec(f"index = widget.{ecombobox}.findText(d['{ecombobox}'])")
					exec(f"if index != -1: widget.{ecombobox}.setCurrentIndex(index)")
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
	setA(widget)

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
		'special_case',
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
			'second_earthquake_properties_drifts',
			'special_case',
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
		# New version
		'tx_an',
		'ty_an',
		'tx1_an',
		'ty1_an',
		'tx_all_an',
		'ty_all_an',
		):
		if key in keys and hasattr(widget, key):
			exec(f"widget.{key}.setValue(d['{key}'])")
	# TreeViewes
	set_system_treeview(widget)
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

def set_system_treeview(widget):
	items = {}

	# Set some random data:
	csv_path =  civiltools_path / 'db' / 'systems.csv'
	with open(csv_path, 'r', encoding='utf-8') as f:
		reader = csv.reader(f, delimiter=',')
		for row in reader:
			if (
				row[0][1] in ['ا', 'ب', 'پ', 'ت', 'ث'] or
				row[0][0] in ['ا', 'ب', 'پ', 'ت', 'ث']
				):
				i = row[0]
				root = treeview_system.CustomNode(i)
				items[i] = root
			else:
				root.addChild(treeview_system.CustomNode(row))
	headers = ('System', 'Ru', 'Omega', 'Cd', 'H_max', 'alpha', 'beta', 'note', 'ID')
	if hasattr(widget, 'x_treeview'):
		widget.x_treeview.setModel(treeview_system.CustomModel(list(items.values()), headers=headers))
		widget.x_treeview.setColumnWidth(0, 400)
		for i in range(1,len(headers)):
			widget.x_treeview.setColumnWidth(i, 40)
	if hasattr(widget, 'y_treeview'):
		widget.y_treeview.setModel(treeview_system.CustomModel(list(items.values()), headers=headers))
		widget.y_treeview.setColumnWidth(0, 400)
		for i in range(1,len(headers)):
			widget.y_treeview.setColumnWidth(i, 40)
	# second system
	if hasattr(widget, 'x_treeview_1'):
		widget.x_treeview_1.setModel(treeview_system.CustomModel(list(items.values()), headers=headers))
		widget.x_treeview_1.setColumnWidth(0, 400)
		for i in range(1,len(headers)):
			widget.x_treeview_1.setColumnWidth(i, 40)
	if hasattr(widget, 'y_treeview_1'):
		widget.y_treeview_1.setModel(treeview_system.CustomModel(list(items.values()), headers=headers))
		widget.y_treeview_1.setColumnWidth(0, 400)
		for i in range(1,len(headers)):
			widget.y_treeview_1.setColumnWidth(i, 40)

def fill_cities(widget):
	if hasattr(widget, 'ostan'):
		ostans = ostanha.ostans.keys()
		widget.ostan.addItems(ostans)

def fill_top_bot_stories(etabs, widget):
	stories = etabs.SapModel.Story.GetStories()[1]
	for combo_box in (
		'bot_x_combo',
		'top_x_combo',
		'top_story_for_height',
		'bot_x1_combo',
		'top_x1_combo',
		'top_story_for_height1',
	):
		if hasattr(widget, combo_box):
			exec(f'widget.{combo_box}.addItems(stories)')
	n = len(stories)
	if hasattr(widget, 'bot_x_combo'):
		widget.bot_x_combo.setCurrentIndex(0)
	if hasattr(widget, 'top_x_combo'):
		widget.top_x_combo.setCurrentIndex(n - 1)
	if hasattr(widget, 'top_story_for_height'):
		if n > 1:
			widget.top_story_for_height.setCurrentIndex(n - 2)
		else:
			widget.top_story_for_height.setCurrentIndex(n - 1)

def fill_height_and_no_of_stories(etabs, widget):
	if hasattr(widget, 'height_x') and hasattr(widget, 'no_of_story_x'):
		if widget.top_story_for_height_checkbox.isChecked():
			widget.top_story_for_height.setEnabled(True)
			top_story_x = top_story_y = widget.top_story_for_height.currentText()
		else:
			widget.top_story_for_height.setEnabled(False)
			top_story_x = top_story_y = widget.top_x_combo.currentText()
		bot_story_x = bot_story_y = widget.bot_x_combo.currentText()
		bot_level_x, top_level_x, bot_level_y, top_level_y = etabs.story.get_top_bot_levels(
				bot_story_x, top_story_x, bot_story_y, top_story_y, False
				)
		hx, _ = etabs.story.get_heights(bot_story_x, top_story_x, bot_story_y, top_story_y, False)
		nx, _ = etabs.story.get_no_of_stories(bot_level_x, top_level_x, bot_level_y, top_level_y)
		widget.no_of_story_x.setValue(nx)
		widget.height_x.setValue(hx)


def get_current_ostan(widget):
	return widget.ostan.currentText()

def get_current_city(widget):
	return widget.city.currentText()

def get_citys_of_current_ostan(ostan):
	'''return citys of ostan'''
	return ostanha.ostans[ostan].keys()

def setA(widget):
	if hasattr(widget, 'risk_level'):
		sotoh = ['خیلی زیاد', 'زیاد', 'متوسط', 'کم']
		ostan = get_current_ostan(widget)
		city = get_current_city(widget)
		try:
			A = int(ostanha.ostans[ostan][city][0])
			i = widget.risk_level.findText(sotoh[A - 1])
			widget.risk_level.setCurrentIndex(i)
		except KeyError:
			pass

def current_building_from_etabs(etabs):
	d = get_settings_from_etabs(etabs)
	risk_level = d['risk_level']
	importance_factor = float(d['importance_factor'])
	soil = d['soil_type']
	city = d['city']
	height_x = d['height_x']
	no_story = d['no_of_story_x']
	x_systemtype = d['x_system_name']
	x_lateraltype = d['x_lateral_name']
	y_systemtype = d['y_system_name']
	y_lateraltype = d['y_lateral_name']
	is_infill = d['infill']
	x_system = StructureSystem(x_systemtype, x_lateraltype, "X")
	y_system = StructureSystem(y_systemtype, y_lateraltype, "Y")
	# Second System
	two_system = d.get('activate_second_system', False)
	height_x1 = d.get('height_x1', 0)
	no_story1 = d.get('no_of_story_x1', 0)
	is_infill1= d.get('infill_1', False)
	if two_system:
		x_systemtype1 = d['x_system_name_1']
		x_lateraltype1 = d['x_lateral_name_1']
		y_systemtype1 = d['y_system_name_1']
		y_lateraltype1 = d['y_lateral_name_1']
		x_system1 = StructureSystem(x_systemtype1, x_lateraltype1, "X")
		y_system1 = StructureSystem(y_systemtype1, y_lateraltype1, "Y")
	else:
		x_system1 = None
		y_system1 = None
	# Analytical Periods
	tx = d.get('tx_an', d.get('t_an_x', 4))
	ty = d.get('ty_an', d.get('t_an_y', 4))
	tx1_an = d.get('tx1_an', d.get('t_an_x1', 4))
	ty1_an = d.get('ty1_an', d.get('t_an_y1', 4))
	tx_all_an = d.get('tx_all_an', 4)
	ty_all_an = d.get('ty_all_an', 4)
	#     if 
	#     no_of_stories = d['no_of_story_x'] + d['no_of_story_x1']
	build = Building(
				risk_level,
				importance_factor,
				soil,
				city,
				no_story,
				height_x,
				is_infill,
				x_system,
				y_system,
				tx,
				ty,
				x_system1,
				y_system1,
				height_x1,
				is_infill1,
				no_story1,
				tx1_an,
				ty1_an,
				tx_all_an,
				ty_all_an,
				)
	return build

def current_building_from_widget(widget):
	x_system = get_system(widget.x_treeview)
	y_system = get_system(widget.y_treeview)
	if x_system is None or y_system is None:
		return None
	risk_level = widget.risk_level.currentText()
	city = widget.city.currentText()
	soil = widget.soil_type.currentText()
	importance_factor = float(widget.importance_factor.currentText())
	height_x = widget.height_x.value()
	no_of_story = widget.no_of_story_x.value()
	is_infill = widget.infill.isChecked()
	height_2 = widget.height_x1.value()
	no_of_story_2 = widget.no_of_story_x1.value()
	is_infill_2 = widget.infill_1.isChecked()
	if widget.activate_second_system.isChecked():
		x_system_2 = get_system(widget.x_treeview_1)
		y_system_2 = get_system(widget.y_treeview_1)
	else:
		x_system_2, y_system_2 = (None, None)
	tx_an = 4
	ty_an = 4
	tx1_an = 4
	ty1_an = 4
	tx_all_an = 4
	ty_all_an = 4
	if hasattr(widget, 'tx_an'):
		tx_an = widget.tx_an.value()
	if hasattr(widget, 'ty_an'):
		ty_an = widget.ty_an.value()
	if hasattr(widget, 'tx1_an'):
		tx1_an = widget.tx1_an.value()
	if hasattr(widget, 'ty1_an'):
		ty1_an = widget.ty1_an.value()
	if hasattr(widget, 'tx_all_an'):
		tx_all_an = widget.tx_all_an.value()
	if hasattr(widget, 'ty_all_an'):
		ty_all_an = widget.ty_all_an.value()
	build = Building(
				risk_level,
				importance_factor,
				soil,
				city,
				no_of_story,
				height_x,
				is_infill,
				x_system,
				y_system,
				tx_an,
				ty_an,
				# Second System
				x_system_2= x_system_2,
				y_system_2= y_system_2,
				height_2 = height_2,
				is_infill_2= is_infill_2,
				number_of_story_2= no_of_story_2,
				tx_an_2=tx1_an,
				ty_an_2=ty1_an,
				tx_an_all=tx_all_an,
				ty_an_all=ty_all_an,
	)
	return build

def get_system(view):
	ret = get_treeview_item_prop(view)
	if ret is None:
		return
	system, lateral, *_ = ret
	if 'x' in view.objectName():
		system = StructureSystem(system, lateral, 'X')
	elif 'y' in view.objectName():
		system = StructureSystem(system, lateral, 'Y')
	return system


