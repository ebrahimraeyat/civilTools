class Results:
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

    def get_xy_period(self):
        if not self.SapModel.GetModelIsLocked():
            self.SapModel.analyze.RunAnalysis()
        modal_name = self.etabs.load_cases.get_modal_loadcase_name()
        self.SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
        self.SapModel.Results.Setup.SetCaseSelectedForOutput(modal_name)
        ux = self.SapModel.Results.ModalParticipatingMassRatios()[5]
        uy = self.SapModel.Results.ModalParticipatingMassRatios()[6]
        x_index = ux.index(max(ux))
        y_index = uy.index(max(uy))
        periods = self.SapModel.Results.ModalParticipatingMassRatios()[4]
        Tx = periods[x_index]
        Ty = periods[y_index]
        return Tx, Ty, x_index + 1, y_index + 1

    def get_xy_frequency(self):
        Tx, Ty, i_x, i_y = self.get_xy_period()
        from math import pi
        return (2 * pi / Tx, 2 * pi / Ty, i_x, i_y)

    def get_point_xy_displacement(self, point_name, lp_name):
        self.SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
        self.SapModel.Results.Setup.SetCaseSelectedForOutput(lp_name)
        results = self.SapModel.Results.JointDispl(point_name, 0)
        x = results[6][0]
        y = results[7][0]
        return x, y

    def get_base_react(self):
        self.SapModel.SetPresentUnits_2(5, 6, 2)
        self.etabs.run_analysis()
        loadcases = self.etabs.load_patterns.get_ex_ey_earthquake_name()
        self.SapModel.Results.Setup.SetCaseSelectedForOutput(loadcases[0])
        self.SapModel.Results.Setup.SetCaseSelectedForOutput(loadcases[1])
        base_react = self.SapModel.Results.BaseReact()
        vx = base_react[4][0]
        vy = base_react[5][1]
        return vx, vy
