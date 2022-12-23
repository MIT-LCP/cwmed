import pandas as pd
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
    target_column = vocab.target_vocab_value
    snomed_target_code = vocab.target_table[target_column].iloc[0]
    expected_target_code = '111839008'  
    assert expected_target_code == snomed_target_code
