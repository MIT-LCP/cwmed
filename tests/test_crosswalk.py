import pandas as pd
import crosswalk as cw

def test_crosswalk_between_icd10_snomed():
    """
    Test that the source code, e.g. icd10 code of ''A04.4'' from the source file 
    is mapped to the expected target standardized code, e.g. snomed code, '111839008'
    in the source to target file.
    """
    vocab = cw.VocabTranslator('tests/data/source_icd10.csv','icd10','tests/data/concept_example_icd10_snomed.csv','ICD10CM','SNOMED','tests/data/concept_relationship_example_icd10_snomed.csv')
    icd10_source_code = vocab.source_voc[vocab.source_voc.icd10 == 'A04.4']['icd10'].iloc[0]
    snomed_target_code = vocab.rel_target_merge[vocab.rel_target_merge.icd10 == icd10_source_code]['SNOMED'].iloc[0]
    expected_target_code = '111839008'  
    assert expected_target_code == snomed_target_code