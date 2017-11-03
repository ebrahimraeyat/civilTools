import unittest
import pandas as pd
from ..readrecord import ReadRecord
from ..processrecord import ProcessRecord, EnsembleRecord


class ReadRecordTest(unittest.TestCase):
    def setUp(self):
        self.read_record = ReadRecord('/home/ebi/olomTahghighat/random/PEERNGARecords_Unscaled/RSN127_FRIULI_BUI-UP.AT2')
        self.read_record.extract_record_prop()

    def test_dt_must_be_read_correct_from_file(self):
        self.assertAlmostEqual(.00244, self.read_record.info_dict['dt'], delta=.000001)

    def test_number_of_points_must_be_read_correct_from_file(self):
        self.assertEqual(7769, self.read_record.info_dict['number_of_points'])

    def test_earthquake_name_must_be_read_correct_from_file(self):
        self.assertEqual('Fruili Italy-03', self.read_record.info_dict['name'])

    def test_date_must_be_read_correct_from_file(self):
        self.assertEqual(' 9/11/1976', self.read_record.info_dict['date'])

    def test_station_must_be_read_correct_from_file(self):
        self.assertEqual(' Buia', self.read_record.info_dict['station'])

    def test_angle_must_be_read_correct_from_file(self):
        self.assertEqual(' UP', self.read_record.info_dict['angle'][:3])


class ProcessRecordTest(unittest.TestCase):

    def setUp(self):
        self.read_record = ReadRecord('/home/ebi/python/civilTools/civilTools/RSN139_TABAS_DAY-L1.AT2')
        self.read_record.extract_record_prop()
        self.processrecord = ProcessRecord(self.read_record, dx=.05)

    def test_number_of_points_after_remove_none_value(self):
        self.assertEqual(self.processrecord.n, 1050)

    def test_shape_of_time_history_record(self):
        self.assertEqual(self.processrecord.time_history_record.shape, (1050, 1))

    def test_distribute_function_must_converge_to_one(self):
        self.assertAlmostEqual(self.processrecord.distribute_function()[0][-1], 1., delta=.01)

    def test_temporal_mean_value_that_calculate_from_density_function(self):
        self.assertAlmostEqual(self.processrecord.temporal_mean_df(), 6.35430158e-05, delta=.00001)

    def test_temporal_mean_value(self):
        self.assertAlmostEqual(self.processrecord.temporal_mean(), 1.3711575047611543e-06, delta=0.000001)


class EnsembleRecordTest(unittest.TestCase):

    def setUp(self):
        read_record_1 = ReadRecord('/home/ebi/python/civilTools/civilTools/RSN139_TABAS_DAY-L1.AT2')
        read_record_2 = ReadRecord('/home/ebi/olomTahghighat/random/PEERNGARecords_Unscaled/RSN1856_YOUNTVL_0732A180.AT2')
        read_records = [read_record_1, read_record_2]
        process_records = []
        for record in read_records:
            process_records.append(ProcessRecord(record))
        self.ensemblerecord = EnsembleRecord(process_records)

    def test_number_of_records(self):
        self.assertEqual(self.ensemblerecord.number_of_records, 2)

    def test_length_of_all_record_must_be_the_same(self):
        self.assertEqual(self.ensemblerecord.number_of_points, 11000)

    def test_all_process_records_must_have_same_points_length(self):
        for ensemble_record in self.ensemblerecord.ensemble_records:
            self.assertEqual(ensemble_record.n, 11000)













