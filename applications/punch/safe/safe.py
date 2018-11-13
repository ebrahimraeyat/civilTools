from collections import namedtuple
import pandas as pd



class Safe:
	__bool = {'Yes': True, 'No': False}

	def __init__(self, filename):
		self.filename = filename
		self.excel = None
		self.access = None
		self.read_file()

	def read_file(self):
		if self.filename.endswith((".xls", ".xlsx")):
			self.excel = pd.read_excel(self.filename, sheetname=None, skiprows=[0,2])
		elif self.filename.endswith((".mdb", ".accdb")):
			#TODO
			pass

	def program_control(self):
		if self.excel is not None:
			program_control = self.excel["Program Control"]
		elif self.access:
			# TODO
			pass

		self.program_name = program_control["ProgramName"][0]
		self.version = program_control["Version"][0]
		UNITS = namedtuple("UNITS", 'force length temp')
		curr_units = program_control["CurrUnits"][0].split(",")
		self.curr_units = UNITS._make(curr_units)
		self.concrete_code = program_control["ConcCode"][0]

	def obj_geom_points(self):
		obj_geom_points = self.excel['Obj Geom - Point Coordinates']
		POINTS = namedtuple("POINTS", 'x y z special')
		point_props = {}
		for _, row in obj_geom_points.iterrows():
			_id = row['Point']
			x = row['GlobalX']
			y = row['GlobalY']
			z = row['GlobalZ']
			special = self.__bool[row['SpecialPt']]
			curr_points = (x, y, z, special)
			point_props[_id] = POINTS._make(curr_points)
		return point_props

	def obj_geom_areas(self):
		obj_geom_areas = self.excel['Obj Geom - Areas 01 - General']
		areas_prop = {}
		for _, row in obj_geom_areas.iterrows():
			_id = row['Area']
			points = (row['Point1'], row['Point2'], row['Point3'], row['Point4'])
			areas_prop[_id] = points
		return areas_prop

if __name__ == '__main__':
	safe = Safe("sattari_safe.xlsx")
	safe.program_control()




