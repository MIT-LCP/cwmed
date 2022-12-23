import pandas as pd
import crosswalk as cw
from pandas.testing import assert_frame_equal

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
    target_column = vocab.target_vocab_value
    snomed_target_code = vocab.target_table[target_column].iloc[0]
    expected_target_code = '111839008'  
    assert expected_target_code == snomed_target_code

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
