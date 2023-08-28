import os
import tempfile
import unittest

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
import filecmp

import cwmed as cw

class TestCW(unittest.TestCase):
    
    def setUp(self):
        self.vocab = cw.VocabTranslator(source_filepath = 'tests/data/input/icd10.csv',
                        source_code_col = 'icd10',
                        concept_filepath = 'tests/data/input/icd10_to_snomed_concept.csv',
                        source_vocab_value = 'ICD10CM',
                        target_vocab_value = 'SNOMED',
                        concept_relationship_filepath = 'tests/data/input/icd10_to_snomed_concept_relationship.csv')
        self.temp_directory = tempfile.TemporaryDirectory()
        self.temp_path_to_directory = self.temp_directory.name
        self.output_file = 'output.csv'
        self.output_path = os.path.join(self.temp_path_to_directory,self.output_file)

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_crosswalk_between_icd10_snomed(self):
        """
        Test that the source code, e.g. icd10 code of 'A04.4' from the source file 
        is mapped to the expected target standardized code, e.g. snomed code, '111839008'
        in the source to target file.
        """
        target_df = self.vocab.target_table
        target_column = self.vocab.target_vocab_value
        source_column = self.vocab.source_vocab_value
        target_row = target_df.loc[target_df[source_column] == 'A04.4']
        snomed_target_code = target_row[target_column].values
        expected_target_code = ['111839008']
        self.assertEqual(expected_target_code, snomed_target_code)

    def test_save_source_to_target_function(self):
        """ 
        Tests that the saved source to target dataframe for icd10 code 'A04.4' 
        and snomed code '111839008' is equal to the expected dataframe.
        """
        self.vocab.save_source_to_target(self.output_path)
        result = pd.read_csv(self.output_path)
        source_column = self.vocab.source_vocab_value
        result = result.loc[result[source_column] == 'A04.4']
        expected = pd.read_csv('tests/data/expected/icd10_to_snomed.csv')
        expected = expected.loc[expected[source_column] == 'A04.4']
        self._compare_csvfiles(self.output_path,'tests/data/expected/icd10_to_snomed.csv')
        assert_frame_equal(result, expected)

    def test_save_source_to_target_failed_mappings_function(self):
        """
        Tests that the dataframe containing source code e.g. icd10 of 'C78.7' from the source file 
        has failed to map to a snomed code as part of the failed mappings csv.
        """ 
        self.vocab.save_source_to_target_failed_mappings(self.output_path)
        result = pd.read_csv(self.output_path)
        source_column = self.vocab.source_vocab_value
        result = result.loc[result[source_column] == 'C78.7']
        expected = pd.read_csv('tests/data/expected/icd10_to_snomed_failed_mappings.csv')
        expected = expected.loc[expected[source_column] == 'C78.7']
        self._compare_csvfiles(self.output_path,'tests/data/expected/icd10_to_snomed_failed_mappings.csv')
        assert_frame_equal(result, expected)

    def _compare_csvfiles(self,file1,file2):
        self.assertTrue(filecmp.cmp(file1, file2))

    def test_get_unique_vocab_returns_expected_output_as_np_ndarray(self):
        """
        Test the get_unique_vocab function from the
        cw module. It asserts that the output of the function is of the same
        type and has the same elements as the expected output, which is an array
        containing the strings 'ICD10CM' and 'SNOMED'. The function is passed the
        file path 'tests/data/input/icd10_to_snomed_concept.csv' as an argument.
        """
        expected_output = np.array(['ICD10CM', 'SNOMED'])
        filepath = 'tests/data/input/icd10_to_snomed_concept.csv'
        output = cw.get_unique_vocab(filepath)
        assert (type(expected_output) == type(output) and
                np.array_equal(expected_output, output))

if __name__=='__main__':
    unittest.main()