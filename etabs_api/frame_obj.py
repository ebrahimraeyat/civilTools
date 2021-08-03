class FrameObj:
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

    def get_beams_columns(
            self,
            type_=2,
            ):
        '''
        type_: 1=steel and 2=concrete
        '''
        beams = []
        columns = []
        others = []
        for label in self.SapModel.FrameObj.GetLabelNameList()[1]:
            if self.SapModel.FrameObj.GetDesignProcedure(label)[0] == type_: 
                if self.SapModel.FrameObj.GetDesignOrientation(label)[0] == 1:
                    columns.append(label)
                elif self.SapModel.FrameObj.GetDesignOrientation(label)[0] == 2:
                    beams.append(label)
                else:
                    others.append(label)
        return beams, columns