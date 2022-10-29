import pandas as pd

def test_crosswalk_between_ndc_rxnorm():
    """
    Test that the source code, e.g. ndc code of'00074798427' from the source file 
    is mapped to the expected target standardized code, e.g. rxnorm code, '313002'
    in the source to target file.
    """
    expected_target_code = int(313002) 

    target_voc_df = pd.read_csv('source_to_target_example.csv',converters={'ndc': str})
    target_code = target_voc_df[target_voc_df.ndc=='00074798427']['RxNorm'].iloc[0]

    assert expected_target_code == target_code
