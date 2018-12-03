import json

def save(widget, json_file):
	d = {}
	d['ostan'] = widget.ostanBox.currentText()
	d['shahr'] = widget.shahrBox.currentText()
	d['soil_type'] = widget.soilType.currentText()
	d['importance_factor'] = widget.IBox.currentText()
	d['height'] = widget.HSpinBox.value()
	d['no_of_story'] = widget.storySpinBox.value()
	d['t_an_x'] = widget.xTAnalaticalSpinBox.value()
	d['t_an_y'] = widget.yTAnalaticalSpinBox.value()
	d['infill'] = widget.infillCheckBox.isChecked()

	# print(dir(index))
	# print(type(index))
	# print(index.parent().data(), index.row(), index.column(), index.data())
	# print(dir(index.parent()))
	# d['x_system'] = widget.x_treeWidget.indexOfTopLevelItem(widget.x_treeWidget.currentItem().parent())
	# d['x_lateral'] = widget.x_treeWidget.currentItem().parent().indexOfChild(widget.x_treeWidget.currentItem())
	# d['y_system'] = widget.y_treeWidget.indexOfTopLevelItem(widget.y_treeWidget.currentItem().parent())
	# d['y_lateral'] = widget.y_treeWidget.currentItem().parent().indexOfChild(widget.y_treeWidget.currentItem())

	with open(json_file, 'w') as f:
		json.dump(d, f)

def load(widget, json_file):
	with open(json_file, 'r') as f:
		d = json.load(f)

	index = widget.ostanBox.findText(d['ostan'])
	widget.ostanBox.setCurrentIndex(index)
	index = widget.shahrBox.findText(d['shahr'])
	widget.shahrBox.setCurrentIndex(index)
	index = widget.soilType.findText(d['soil_type'])
	widget.soilType.setCurrentIndex(index)
	index = widget.IBox.findText(d['importance_factor'])
	widget.IBox.setCurrentIndex(index)
	widget.HSpinBox.setValue(d['height'])
	widget.storySpinBox.setValue(d['no_of_story'])
	widget.xTAnalaticalSpinBox.setValue(d['t_an_x'])
	widget.yTAnalaticalSpinBox.setValue(d['t_an_y'])
	widget.infillCheckBox.setChecked(d['infill'])

