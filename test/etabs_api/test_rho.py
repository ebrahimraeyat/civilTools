



# def test_get_stories_with_shear_greater_than_35_base_shear(shayesteh):
#     SapModel = shayesteh.SapModel
#     stories = rho.get_stories_with_shear_greater_than_35_base_shear(
#         SapModel, 'QX')
#     assert stories == ['STORY4', 'STORY3', 'STORY2', 'STORY1']




def test_multiply_seismic_loads(shayesteh):
    NumFatalErrors, ret = rho.multiply_seismic_loads(shayesteh.SapModel, .67, .5)
    assert NumFatalErrors == 0
    assert ret == 0

def test_set_end_release_frame(shayesteh):
    er = rho.set_end_release_frame(shayesteh.SapModel, '115')
    ENDRELEASE = [(False, False, False, True, True, True),
                  (False, False, False, False, True, True),
                  (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                  (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 0]
    assert er == ENDRELEASE



def test_set_frame_obj_selected_in_story(nazari):
    SapModel = nazari.SapModel
    frames = rho.set_frame_obj_selected_in_story(SapModel, 'Story1')
    assert len(frames) == 32



def test_get_point_xy_displacement(nazari):
    SapModel = nazari.SapModel
    x, y = rho.get_point_xy_displacement(SapModel, '1', 'EX')
    assert pytest.approx(x, abs=.1) == 36
    assert pytest.approx(y, abs=.01) == -7.38

def test_fix_below_stories(nazari):
    SapModel = nazari.SapModel
    rho.fix_below_stories(SapModel, 'Story3')
    assert True


@pytest.mark.setmethod
def test_set_load_cases_to_analyze(nazari):
    SapModel = nazari.SapModel
    rho.set_load_cases_to_analyze(SapModel, ('Modal',))
    flags = SapModel.Analyze.GetRunCaseFlag(0)
    load_cases = flags[1]
    runs = flags[2]
    for lc, run in zip(load_cases, runs):
        if lc != 'Modal':
            assert not run
        else:
            assert run
    rho.set_load_cases_to_analyze(SapModel, 'All')
    flags = SapModel.Analyze.GetRunCaseFlag(0)
    runs = flags[2]
    for run in runs:
        assert run


if __name__ == '__main__':
    etabs = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
    SapModel = etabs.SapModel
    print('')
    
    

