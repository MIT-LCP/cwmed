from crosswalk import Standard_vocab_translator

def test_crosswalk():
    """
    Test that the crosswalk is working.
    """
    test = Standard_vocab_translator('NDC','RxNorm','source_2.csv','ndc')
    ndc_source=test.source_voc.ndc[16]
    ndc_source
    rxnorm_out_column=test.rel_target_merge[test.rel_target_merge.ndc==ndc_source]['RxNorm'].iloc[0]
    rxnorm_out_column
    expected_rxnorm = '313002'
    assert expected_rxnorm == rxnorm_out_column