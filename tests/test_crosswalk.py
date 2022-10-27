import pytest

from crosswalk import VocabTranslator

def test_crosswalk_between_ndc_rxnorm():
    """
    Test that an ndc code from the source file is mapped to the expected rxnorm code in the common vocabulary.
    """
    vocab = VocabTranslator('NDC','RxNorm','source_2.csv','ndc')
    ndc_source = vocab.source_voc.ndc[16]
    rxnorm_code = vocab.rel_target_merge[vocab.rel_target_merge.ndc==ndc_source]['RxNorm'].iloc[0]
    expected_rxnorm = '313002'
    assert expected_rxnorm == rxnorm_code
