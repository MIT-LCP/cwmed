import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

import crosswalk as cw

def test_crosswalk_between_icd10_snomed():
    """
    Test that the source code, e.g. icd10 code of 'A04.4' from the source file 
    is mapped to the expected target standardized code, e.g. snomed code, '111839008'
    in the source to target file.
    """
    vocab = cw.VocabTranslator(source_filepath = 'tests/data/source_icd10.csv',
                               source_code_col = 'icd10',
                               concept_filepath = 'tests/data/concept_example_icd10_snomed.csv',
                               source_vocab_value = 'ICD10CM',
                               target_vocab_value = 'SNOMED',
                               concept_relationship_filepath = 'tests/data/concept_relationship_example_icd10_snomed.csv')
    target_df = vocab.target_table
    target_column = vocab.target_vocab_value
    source_column = vocab.source_code_col
    target_row = target_df.loc[target_df[source_column] == 'A04.4']
    snomed_target_code = target_row[target_column].values
    expected_target_code = ['111839008']
    assert (expected_target_code == snomed_target_code)

def test_save_dic_function():
    """ 
    Tests that the saved source to target dataframe for icd10 code 'A04.4' 
    and snomed code '111839008' is equal to the expected dataframe.
    """
    vocab = cw.VocabTranslator(source_filepath = 'tests/data/source_icd10.csv',
                               source_code_col = 'icd10',
                               concept_filepath = 'tests/data/concept_example_icd10_snomed.csv',
                               source_vocab_value = 'ICD10CM',target_vocab_value = 'SNOMED',
                               concept_relationship_filepath = 'tests/data/concept_relationship_example_icd10_snomed.csv')
    vocab.save_dic('tests/data/source_icd10_to_snomed_example.csv')
    icd10_to_snomed_target_df = pd.read_csv('tests/data/source_icd10_to_snomed_example.csv')
    icd10_to_snomed_target_df_filtered = icd10_to_snomed_target_df.loc[icd10_to_snomed_target_df['icd10'] == 'A04.4']
    expected_target_df = pd.read_csv('tests/data/source_icd10_to_snomed_example_expected_result.csv')
    expected_target_df_filtered = expected_target_df.loc[icd10_to_snomed_target_df['icd10'] == 'A04.4']
    assert_frame_equal(expected_target_df_filtered,icd10_to_snomed_target_df_filtered, check_dtype= False)

def test_failed_mappings_function():
    """
    Tests that the dataframe containing source code e.g. icd10 of 'C78.7' from the source file 
    has failed to map to a snomed code as part of the failed mappings csv.
    """
    vocab = cw.VocabTranslator(source_filepath = 'tests/data/source_icd10.csv',
                               source_code_col = 'icd10',
                               concept_filepath = 'tests/data/concept_example_icd10_snomed.csv',
                               source_vocab_value = 'ICD10CM',target_vocab_value = 'SNOMED',
                               concept_relationship_filepath = 'tests/data/concept_relationship_example_icd10_snomed.csv')
    vocab.failed_mappings('tests/data/source_icd10_to_snomed_failed_mappings_example.csv')
    icd10_to_snomed_target_df_failed_mappings = pd.read_csv('tests/data/source_icd10_to_snomed_failed_mappings_example.csv')
    icd10_to_snomed_target_df_failed_mappings_filtered = icd10_to_snomed_target_df_failed_mappings.loc[icd10_to_snomed_target_df_failed_mappings['icd10'] == 'C78.7']   
    expected_target_df = pd.read_csv('tests/data/source_icd10_to_snomed_failed_mappings_example_expected_result.csv') 
    expected_target_df_filtered = expected_target_df.loc[expected_target_df['icd10'] == 'C78.7']   
    assert_frame_equal(expected_target_df_filtered,icd10_to_snomed_target_df_failed_mappings_filtered, check_dtype= False)


def test_check_concept_file_source_target_values_returns_expected_output_as_np_ndarray():
    """
    Test the check_concept_file_source_target_values function from the
    cw module. It asserts that the output of the function is of the same
    type and has the same elements as the expected output, which is an array
    containing the strings 'ICD10CM' and 'SNOMED'. The function is passed the
    file path 'tests/data/concept_example_icd10_snomed.csv' as an argument.
    """
    expected_output = np.array(['ICD10CM', 'SNOMED'])
    filepath = 'tests/data/concept_example_icd10_snomed.csv'
    output = cw.check_concept_file_source_target_values(filepath)
    assert (type(expected_output) == type(output) and
            np.array_equal(expected_output, output))
