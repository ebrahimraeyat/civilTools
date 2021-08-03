__all__ = ['View']


class View:
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

    def show_point(
            self,
            story : str,
            label : str,
            ):
        self.SapModel.SelectObj.ClearSelection()
        name = self.SapModel.PointObj.GetNameFromLabel(label, story)[0]
        self.SapModel.PointObj.SetSelected(name, True)
        self.SapModel.View.RefreshView()
        return True