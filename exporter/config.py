import json

def save(json_file, widget):
	d = {}
	d['ostan'] = widget.ostanBox.currentText()
	d['city'] = widget.cityBox.currentText()
	d['risk_level'] = widget.accText.text()
	d['soil_type'] = widget.soilType.currentText()
	d['importance_factor'] = widget.IBox.currentText()
	d['bot_x_combo'] = widget.bot_x_combo.currentText()
	d['top_x_combo'] = widget.top_x_combo.currentText()
	d['height_x'] = widget.height_x_spinbox.value()
	d['no_of_story_x'] = widget.no_story_x_spinbox.value()
	# d['t_an_x'] = widget.xTAnalaticalSpinBox.value()
	# d['t_an_y'] = widget.yTAnalaticalSpinBox.value()
	d['infill'] = widget.infillCheckBox.isChecked()
	d['x_system'] = find_selected_item_in_treewidget(widget.x_treeWidget)
	d['y_system'] = find_selected_item_in_treewidget(widget.y_treeWidget)
	d['x_system_name'] = widget.x_treeWidget.currentItem().parent().text(0)
	d['x_lateral_name'] = widget.x_treeWidget.currentItem().text(0)
	d['y_system_name'] = widget.y_treeWidget.currentItem().parent().text(0)
	d['y_lateral_name'] = widget.y_treeWidget.currentItem().text(0)
	with open(json_file, 'w') as f:
		json.dump(d, f)

def save_analytical_periods(json_file, tx, ty):
	with open(json_file, 'r') as f:
		d = json.load(f)
	d['t_an_x'] = tx
	d['t_an_y'] = ty
	with open(json_file, 'w') as f:
		json.dump(d, f)

def get_analytical_periods(json_file):
	with open(json_file, 'r') as f:
		d = json.load(f)
	tx = d.get('t_an_x', 2)
	ty = d.get('t_an_y', 2)
	return tx, ty

def load(json_file, widget=None):
	with open(json_file, 'r') as f:
		d = json.load(f)
	if widget is None:
		return d

	index = widget.soilType.findText(d['soil_type'])
	widget.soilType.setCurrentIndex(index)
	index = widget.IBox.findText(d['importance_factor'])
	widget.IBox.setCurrentIndex(index)
	index = widget.bot_x_combo.findText(d['bot_x_combo'])
	widget.bot_x_combo.setCurrentIndex(index)
	index = widget.top_x_combo.findText(d['top_x_combo'])
	widget.top_x_combo.setCurrentIndex(index)
	widget.height_x_spinbox.setValue(d['height_x'])
	widget.no_story_x_spinbox.setValue(d['no_of_story_x'])
	# widget.xTAnalaticalSpinBox.setValue(d['t_an_x'])
	# widget.yTAnalaticalSpinBox.setValue(d['t_an_y'])
	widget.infillCheckBox.setChecked(d['infill'])
	x_item = d.get('x_system', None)
	y_item = d.get('y_system', None)
	if x_item and y_item:
		select_treewidget_item(widget.x_treeWidget, *x_item)
		select_treewidget_item(widget.y_treeWidget, *y_item)

def find_selected_item_in_treewidget(treewidget):
	root_item = treewidget.invisibleRootItem()
	top_level_count = root_item.childCount()

	for i in range(top_level_count):
		top_level_item = root_item.child(i)
		child_num = top_level_item.childCount()
		for n in range(child_num):
			child_item = top_level_item.child(n)
			if child_item.isSelected():
				return i, n

def select_treewidget_item(treewidget, i, n):
	if i is None:
		return
	cur_i, cur_n = find_selected_item_in_treewidget(treewidget)
	root_item = treewidget.invisibleRootItem()
	if cur_i == i and cur_n == n:
		return
	else:
		root_item.child(cur_i).child(cur_n).setSelected(False)
		root_item.child(cur_i).setExpanded(False)
		root_item.child(i).child(n).setSelected(True)
		root_item.child(i).setExpanded(True)
