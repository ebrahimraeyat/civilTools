#example of unittest module

#import unittest
#from section import *

#IPE18_2 = {'Z22': 0, 'xm': 91.0, 'I22': 11915795.0, 'bf': 182, 'S22Neg': 130942.8021978022, 'ymax': 180, 'area': 4780, 'tw': 10.6, 'tf': 16.0, 'R33': 74.23247436968558, 'AS3': 2426.666666666667, 'AS2': 1908.0, '_type': '2STEEL_I_SECTION', 'ym': 90.0, 'Z33': 332000, 'I33': 26340000, 'S22Pos': 130942.8021978022, 'S33Pos': 292666.6666666667, 'S33Neg': 292666.6666666667, 'name': '2IPE18', 'h': 360, 'xmax': 182, 'R22': 49.928390142877774}
#IPE20_2 = {'Z22': 0, 'xm': 100.0, 'I22': 17090000.0, 'bf': 200, 'S22Neg': 170900.0, 'ymax': 200, 'area': 5700, 'tw': 11.2, 'tf': 17.0, 'R33': 82.50465164982911, 'AS3': 2833.3333333333335, 'AS2': 2240.0, '_type': '2STEEL_I_SECTION', 'ym': 100.0, 'Z33': 442000, 'I33': 38800000, 'S22Pos': 170900.0, 'S33Pos': 388000.0, 'S33Neg': 388000.0, 'name': '2IPE20', 'h': 400, 'xmax': 200, 'R22': 54.7562381289574}
#IPES2 = [IPE18_2, IPE20_2]


#class TestIpe(unittest.TestCase):

    #def test_Ipe(self):
        #IPES = Ipe.createStandardIpes()
        #IPE18 = IPES[18]
        #IPE20 = IPES[20]
        #IPE18_2 = IPE18.double()
        #IPE20_2 = IPE20.double()
        #IPE2 = [IPE18_2, IPE20_2]
        #for i, Ipe2 in enumerate(IPE2):

            #self.assertEqual(Ipe2.sectionProp, IPES2[i])
            #self.assertEqual(IPE18_2.xm, 91)
            #self.assertEqual(IPE18_2.area, 4780)

    #def test_last(self):
        #self.assertTrue(last(list_chars), 'm')

    #def testFirstAgain(self):
        #self.failUnless(first(list_chars), 'Z')

    #def testLastAgain(self):
        #self.failIf(last(list_nums), 9)



#if __name__ == '__main__':
    #unittest.main()


