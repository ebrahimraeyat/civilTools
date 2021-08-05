class Points:
    def __init__(
                self,
                SapModel=None,
                etabs=None,
                ):
        if not SapModel:
            self.etabs = etabs
            self.SapModel = etabs.SapModel
        else:
            self.SapModel = SapModel

    def set_point_restraint(self,
            point_names,
            restraint: list= [True, True, False, False, False, False]):
        for point_name in point_names:
            self.SapModel.PointObj.SetRestraint(point_name, restraint)