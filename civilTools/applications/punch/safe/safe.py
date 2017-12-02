from collections import namedtuple
import pandas as pd


class Safe:
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

if __name__ == '__main__':
	safe = Safe("sattari_safe.xlsx")
	safe.program_control()




