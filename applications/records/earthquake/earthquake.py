


class Earthquake(object): 

	def __init__(self, x_accelerated=None, y_accelerated=None, z_accelerated=None):
		self.accelerations = {'x': x_accelerated,
							  'y': y_accelerated,
							  'z': z_accelerated}
		self._set_properties()

	def __str__(self):
		s = ''
		s += f"Name:\t{self.name}\n"
		s += f"date:\t{self.date}\n"
		s += f"station:\t{self.station}\n"
		s += f"duration:\t{self.duration}\n"
		s += f"dt:\t{self.dt}\n"
		s += f"NPT:\t{self.number_of_points}\n"
		return s	

	def _set_properties(self):
		self.info = self.accelerations['x'].accelerated_info
		self.name = self.info['name']
		self.dt = self.info['dt']
		self.number_of_points = self.info['number_of_points']
		self.duration = self.dt * self.number_of_points
		self.station = self.info['station']
		self.date = self.info['date']
		# self.eff_duration_index = self.effective_duration_index()
		self.eff_duration = self.effective_duration_index()[0]

	def interpolate_earthquake(self, new_dt):
		for accelerated in self.accelerations.values():
			accelerated.interpolate_acceleration(new_dt)
		self._set_properties()

	def scale(self, sf=1):
		for accelerated in self.accelerations.values():
			accelerated.scale(sf)



	def effective_duration_index(self):
    # ''' calculate effective duration of acceleration with 
    # trifunac algorithm. is based on the mean-square integral
    # of amplitude which is related to the seismic energy content
    # of the ground motion ( Trifunac and Brady, 1975)'''
	    acc = self.accelerations['x']
	    return acc.effective_duration_index()

	def cut(self, duration, start=None):
		if not start:
			start = self.effective_duration_index()[1]
		end = int(start + duration / self.dt)
		for accelerated in self.accelerations.values():
			accelerated.cut(end, start)
		self._set_properties()


if __name__ == '__main__':
	from ..accelerated.processaccelerated import Accelerated as acc
	z_filename = '/home/ebi/olomTahghighat/4/random/PEERNGARecords_Unscaled(1)/RSN88_SFERN_FSD-UP.AT2'
	x_filename = '/home/ebi/olomTahghighat/4/random/PEERNGARecords_Unscaled(1)/RSN88_SFERN_FSD172.AT2'
	y_filename = '/home/ebi/olomTahghighat/4/random/PEERNGARecords_Unscaled(1)/RSN88_SFERN_FSD262.AT2'
	x_accelerated = acc(x_filename)
	y_accelerated = acc(y_filename)
	z_accelerated = acc(z_filename)
	sfern = Earthquake(x_accelerated, y_accelerated, z_accelerated)
	print(sfern)

    



