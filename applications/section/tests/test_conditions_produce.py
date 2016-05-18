import unittest
from resource.produce_conditions import *

class Test_conditions_produce(unittest.TestCase):

    def setUp(self):
        pass

    def test_2IPE_flang_plate_web_plate_beam_high_ductility_conditions(self):

        ifCondition, elseCondition, TF = produce_conditions_from_slender_provision_flange({'bf/(2*tf)': '0.3*w',
                                                                    'B1/t1': '0.55w', 'BF/TF': '0.6*w'})
        self.assertEqual(ifCondition, '0.6*B1*tf/(0.55*bf')


if __name__ == '__main__':
    unittest.main()
