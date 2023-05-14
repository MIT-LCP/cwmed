import numpy as np
import os
import pandas as pd
from pandas.testing import assert_frame_equal
import tempfile

import crosswalk as cw

def test_crosswalk_between_icd10_snomed():
    """
    Test that the source code, e.g. icd10 code of 'A04.4' from the source file 
    is mapped to the expected target standardized code, e.g. snomed code, '111839008'
    in the source to target file.
    """
    vocab = cw.VocabTranslator(source_filepath = 'tests/data/input/icd10.csv',
                               source_code_col = 'icd10',
                               concept_filepath = 'tests/data/input/icd10_to_snomed_concept.csv',
                               source_vocab_value = 'ICD10CM',
                               target_vocab_value = 'SNOMED',
                               concept_relationship_filepath = 'tests/data/input/icd10_to_snomed_concept_relationship.csv')
    target_df = vocab.target_table
    target_column = vocab.target_vocab_value
    source_column = vocab.source_vocab_value
    target_row = target_df.loc[target_df[source_column] == 'A04.4']
    snomed_target_code = target_row[target_column].values
    expected_target_code = ['111839008']
    assert (expected_target_code == snomed_target_code)

def test_save_source_to_target_function():
    """ 
    Tests that the saved source to target dataframe for icd10 code 'A04.4' 
    and snomed code '111839008' is equal to the expected dataframe.
    """
    vocab = cw.VocabTranslator(source_filepath = 'tests/data/input/icd10.csv',
                               source_code_col = 'icd10',
                               concept_filepath = 'tests/data/input/icd10_to_snomed_concept.csv',
                               source_vocab_value = 'ICD10CM',target_vocab_value = 'SNOMED',
                               concept_relationship_filepath = 'tests/data/input/icd10_to_snomed_concept_relationship.csv')
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = os.path.join(tmp_dir,'output.csv')
        vocab.save_source_to_target(tmp_file)
        result = pd.read_csv(tmp_file)
        result = result.loc[result['icd10'] == 'A04.4']
        expected = pd.read_csv('tests/data/source_icd10_to_snomed_example_expected_result.csv')
        expected = expected.loc[expected['icd10'] == 'A04.4']
        assert_frame_equal(result, expected)

def test_save_source_to_target_failed_mappings_function():
    """
    Tests that the dataframe containing source code e.g. icd10 of 'C78.7' from the source file 
    has failed to map to a snomed code as part of the failed mappings csv.
    """ 
    vocab = cw.VocabTranslator(source_filepath = 'tests/data/input/icd10.csv',
                               source_code_col = 'icd10',
                               concept_filepath = 'tests/data/input/icd10_to_snomed_concept.csv',
                               source_vocab_value = 'ICD10CM',target_vocab_value = 'SNOMED',
                               concept_relationship_filepath = 'tests/data/icd10_to_snomed_concept_relationship.csv')
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = os.path.join(tmp_dir,'output.csv')
        vocab.save_source_to_target_failed_mappings(tmp_file)
        result = pd.read_csv(tmp_file) # actual target table
        result = result.loc[result['icd10'] == 'C78.7']
        expected = pd.read_csv('tests/data/source_icd10_to_snomed_failed_mappings_example_expected_result.csv')
        expected = expected.loc[expected['icd10'] == 'C78.7']
        assert_frame_equal(result, expected)


def test_get_unique_vocab_returns_expected_output_as_np_ndarray():
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
