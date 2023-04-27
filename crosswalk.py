import io
import pandas as pd
import requests
import zipfile


def download_data(url, path):
    """
    Download and unzip two required files
    (1) CONCEPT.csv and (2) CONCEPT_RELATIONSHIP.csv
    using the url link emailed to registered users on the Athena OHDSI website.
    
    Args:
        url (str): Url link to download zipfile.
        path (str): Output directory to save CONCEPT.csv and CONCEPT_RELATIONSHIP.csv files.

    Examples:
    >>> import cw
    >>> url="https://example.com/data.zip"
    >>> path = "/path/to/output/directory/"
    >>> cw.download_data(url,path)
    """

    response = requests.get(url) 
    z = zipfile.ZipFile(io.BytesIO(response.content))
    z.extractall(path, members=[i for i in z.namelist()
                 if i in ('CONCEPT.csv', 'CONCEPT_RELATIONSHIP.csv')])

def get_unique_vocab(file_path):
    """
    Get a NumPy array of unique source and target vocab from vocabulary_id column from the CONCEPT.csv file downloaded from Athena.

    Args:
        filepath (str): The file path to CONCEPT.csv.

    Returns:
        numpy.ndarray: A NumPy array of unique values from the vocabulary_id column in CONCEPT.csv.

    Examples:
    
    >>> import cw
    >>> unique_vocabs = cw.get_unique_vocab('tests/data/source_icd10.csv')
    >>> print(unique_vocabs)
    ['ICD10CM', 'SNOMED']

    """

    concepts = pd.read_csv(file_path, sep='\t')

    unique_vocab_values = concepts["vocabulary_id"].unique()

    return unique_vocab_values

class VocabTranslator:
    """
    Translate source vocab to target vocab.

    Requires concept file and concept relationship downloaded from the Athena OHDSI website
    (https://athena.ohdsi.org/auth/login?forceSSO=true).

    Call `get_unique_vocab(filepath)` to use the specific source and target values
    from vocabulary_id column from the concept file
    in the source_vocab_value and target_vocab_value fields.

    Attributes:
        source_filepath (str): Path to source vocabulary file.
        source_code_col (str): Column with source code in the source vocabulary file that will be mapped to the target vocabulary.
        concept_filepath (str): Path to CONCEPT.csv.
        source_vocab_value (str): Value of the source vocabulary.
        target_vocab_value (str): Value of target vocabulary.
        concept_relationship_filepath = Path to CONCEPT_RELATIONSHIP.csv.

    Examples:
    >>> vocab = cw.VocabTranslator(source_filepath = 'tests/data/source_icd10.csv',
                                   source_code_col = 'icd10',
                                   concept_filepath = 'tests/data/concept_example_icd10_snomed.csv',
                                   source_vocab_value = 'ICD10CM',target_vocab_value = 'SNOMED',
                                   concept_relationship_filepath = 'tests/data/concept_relationship_example_icd10_snomed.csv')
    """

    def __init__(self, source_filepath: str, source_code_col: str,
                concept_filepath: str, source_vocab_value: str, target_vocab_value: str,
                concept_relationship_filepath: str):

        self.source_filepath = source_filepath 
        self.source_code_col = source_code_col
        self.concept_filepath = concept_filepath 
        self.source_vocab_value = source_vocab_value
        self.target_vocab_value = target_vocab_value
        self.concept_relationship_filepath = concept_relationship_filepath 
        self.concept_file = self._read_concept_file()
        self.target_table = self._map_source_to_target()

    def _read_source_file(self):
        """
        Read the source file.

        Returns: pd.DataFrame with the source code.

        Examples:
        >>> # Read the source to vocab crosswalk as a Vocab Translator object.
        >>> vocab = cw.VocabTranslator(source_filepath = 'tests/data/source_icd10.csv',
                                       source_code_col = 'icd10',
                                       concept_filepath = 'tests/data/concept_example_icd10_snomed.csv',
                                       source_vocab_value = 'ICD10CM',target_vocab_value = 'SNOMED',
                                       concept_relationship_filepath = 'tests/data/concept_relationship_example_icd10_snomed.csv')
        >>> # Observe the source vocab, e.g. icd10 code 'A04.4' in the source file.
        >>> source_df = vocab._read_source_file()
        >>> source_df[source_df["icd10"] == "A04.4"]
            icd10
        0	A04.4
        """
        df = pd.read_csv(self.source_filepath,
                                converters={self.source_code_col: str})
        return df

    def _read_concept_file(self):
        """
        Read the CONCEPT.csv.

        Returns: pd.DataFrame with a concept_id (an omop id),
                 vocabulary_id that specifices the source or target names,
                 domain_id that defines the clinical domain
                 (e.g. Drugs, conditions, Orocedures, Devices, Observations, Measurements),
                 concept_class_id that describes the vocabulary_id,
                 concept_code that defines the source or target codes,
                 and concept_name that provides the label for the code,
                 and standard_concept that defines whether a vocabulary_id code is standard vocab.

        >>> # Read the source to vocab crosswalk as a Vocab Translator object.
        >>> vocab = cw.VocabTranslator(source_filepath = 'tests/data/source_icd10.csv',
                                       source_code_col = 'icd10',
                                       concept_filepath = 'tests/data/concept_example_icd10_snomed.csv',
                                       source_vocab_value = 'ICD10CM',target_vocab_value = 'SNOMED',
                                       concept_relationship_filepath = 'tests/data/concept_relationship_example_icd10_snomed.csv')
        >>> # Observe the rows with icd 10 source code of A04.4 and snomed standard target code of 111839008 in the CONCEPT.csv.
        >>> concept_df = vocab._read_concept_file()
        >>> concept_df = concept_df[(concept_df['concept_code'] == 'A04.4') | (concept_df['concept_code'] == '111839008')]
        >>> concept_df = concept_df[['concept_id','vocabulary_id','concept_class_id','domain_id','concept_code','concept_name','standard_concept']]
        >>> concept_df
           concept_id	vocabulary_id	concept_class_id	domain_id	concept_code	concept_name	   standard_concept
        0	35205417	ICD10CM	        4-char billing code	Condition	A04.4	        Other intestinal         NaN
                                                                                        Escherichia coli

        1	192815	    SNOMED	        Clinical Finding	Condition	111839008	    Intestinal infection      S
                                                                                        due to E. coli
        """
        df = pd.read_csv(self.concept_filepath, sep='\t',
                                 converters={"concept_id": str,
                                             "concept_code": str})

        # Select only the needed vocabulary_id's, e.g. 'ICD10CM' and 'SNOMED'.
        df = df[(df["vocabulary_id"] == self.source_vocab_value) |
                                (df["vocabulary_id"] == self.target_vocab_value)]

        return df

    def _read_concept_relationship_file(self):
        """
        Read the CONCEPT_RELATIONSHIP.csv which maps source concept-id to target concept-id and vice versa.

        Returns: pd.DataFrame with concept_id_1, concept_id_2 and relationship_id.

        Examples:
        >>> # Read the source to vocab crosswalk as a Vocab Translator object.
        >>> vocab = cw.VocabTranslator(source_filepath = 'tests/data/source_icd10.csv',
                                       source_code_col = 'icd10',
                                       concept_filepath = 'tests/data/concept_example_icd10_snomed.csv',
                                       source_vocab_value = 'ICD10CM',target_vocab_value = 'SNOMED',
                                       concept_relationship_filepath = 'tests/data/concept_relationship_example_icd10_snomed.csv')
        >>> concept_rel_df = vocab._read_concept_relationship_file()
        >>> concept_rel_df = concept_rel_df[concept_rel_df['concept_id_1'] == '35205417']
        >>> concept_rel_df = concept_rel_df[['concept_id_1','concept_id_2', 'relationship_id']]
        >>> concept_rel_df
             concept_id_1	     concept_id_2	relationship_id
        0	  35205417	            192815	            Maps to
        """
        df = pd.read_csv(self.concept_relationship_filepath, sep='\t',
                                              converters={"concept_id_1": str,
                                                          "concept_id_2": str})
        df = df[df['relationship_id'] == "Maps to"]

        return df

    def _map_source_to_source_concept_id (self):
        """
        Map source code to source concept_id in the CONCEPT.csv.

        Returns: pd.DataFrame with the source code, and source concept_id.

        Examples:
        >>> # Read the source to vocab crosswalk as a Vocab Translator object.
        >>> vocab = cw.VocabTranslator(source_filepath = 'tests/data/source_icd10.csv',
                                       source_code_col = 'icd10',
                                       concept_filepath = 'tests/data/concept_example_icd10_snomed.csv',
                                       source_vocab_value = 'ICD10CM',target_vocab_value = 'SNOMED',
                                       concept_relationship_filepath = 'tests/data/concept_relationship_example_icd10_snomed.csv')
        >>> source_to_concept_id_df = vocab._map_source_to_source_concept_id()
        >>> source_to_concept_id_df = source_to_concept_id_df[source_to_concept_id_df['icd10'] == 'A04.4']
        >>> source_to_concept_id_df
         		concept_id	vocabulary_id	concept_class_id	 domain_id	concept_code	 concept_name	   standard_concept
            0	35205417	 ICD10CM	   4-char billing code	 Condition	  A04.4	         Other intestinal         NaN
                                                                                             Escherichia coli
                                                                                             infections                                                                                 infections	
        """
        df = self._read_source_file().merge(self.concept_file, how='left',
                                            left_on=self.source_code_col, 
                                            right_on='concept_code')

        return df

    def _map_source_concept_id_to_target_concept_id (self):
        """
        Map source concept_id to target concept_id in the CONCEPT_RELATIONSHIP.csv.

        Returns: pd.DataFrame with the source code, source concept_id and target concept_id.

        Examples:
        >>> # Read the source to vocab crosswalk as a Vocab Translator object.
        >>> vocab = cw.VocabTranslator(source_filepath = 'tests/data/source_icd10.csv',
                                       source_code_col = 'icd10',
                                       concept_filepath = 'tests/data/concept_example_icd10_snomed.csv',
                                       source_vocab_value = 'ICD10CM',target_vocab_value = 'SNOMED',
                                       concept_relationship_filepath = 'tests/data/concept_relationship_example_icd10_snomed.csv')
        >>> source_concept_id_to_target_concept_id_df = vocab._map_source_concept_id_to_target_concept_id()
        >>> source_concept_id_to_target_concept_id_df = source_concept_id_to_target_concept_id_df[source_concept_id_to_target_concept_id_df['icd10'] == 'A04.4']
        >>> source_concept_id_to_target_concept_id_df
        	icd10   concept_name       concept_id_1       concept_id_2
        0   A04.4    Other intestinal    35205417            192815
                     Escherichia coli
                     infections         
        """
        df = self._map_source_to_source_concept_id().merge(self._read_concept_relationship_file(),
                                                            how='left',
                                                            left_on='concept_id',
                                                            right_on='concept_id_1')

        df = df[[self.source_code_col,
                'concept_name',
                'concept_id_1',
                'concept_id_2']]

        return df

    def _map_source_to_target(self):
        """
        Map source code to target code using target concept_id in the CONCEPT_RELATIONSHIP.csv.

        Returns: pd.DataFrame with the source code, source concept_id and target concept_id.

        Examples:
        >>> # Read the source to vocab crosswalk as a Vocab Translator object.
        >>> vocab = cw.VocabTranslator(source_filepath = 'tests/data/source_icd10.csv',
                                       source_code_col = 'icd10',
                                       concept_filepath = 'tests/data/concept_example_icd10_snomed.csv',
                                       source_vocab_value = 'ICD10CM',target_vocab_value = 'SNOMED',
                                       concept_relationship_filepath = 'tests/data/concept_relationship_example_icd10_snomed.csv')
        >>> source_to_target_df = vocab._map_source_to_target()
        >>> source_to_target_df = source_to_target_df[source_to_target_df['ICD10CM'] == 'A04.4']
        >>> source_to_target_df
        	ICD10CM	 ICD10CM_label	   ICD10CM_omop_id	SNOMED	   SNOMED_label	     SNOMED_omop_id
        0	 A04.4	 Other intestinal    35205417	   111839008    Intestinal           192815
                     Escherichia coli                               infection due
                     infections                                     to E. coli
        """
        df = self._map_source_concept_id_to_target_concept_id().merge(self.concept_file,
                                                                      how='left',
                                                                      left_on="concept_id_2",
                                                                      right_on="concept_id")

        # Select relevant columns from merge tables.
        df = df[[self.source_code_col,
                 'concept_name_x',
                 'concept_id_1',
                 'concept_code',
                 'concept_name_y',
                 'concept_id_2']]

        df.rename(columns={self.source_code_col:self.source_vocab_value},inplace=True)
        df.rename(columns={'concept_name_x':f'{self.source_vocab_value}_label'}, inplace=True)
        df.rename(columns={'concept_id_1':f'{self.source_vocab_value}_omop_id'}, inplace=True)
        df.rename(columns={'concept_code':f'{self.target_vocab_value}'}, inplace=True)
        df.rename(columns={'concept_name_y':f'{self.target_vocab_value}_label'}, inplace=True)
        df.rename(columns={'concept_id_2':f'{self.target_vocab_value}_omop_id'}, inplace=True)

        return df

    def show_source_to_target_table(self):
        """
        Display the source to target table.

        Returns: a pd.DataFrame that maps concepts between the source and target
        vocabularies.

        Examples:
        >>> df = vocab.show_source_to_target_table()
        >>> df = df[df['ICD10CM'] == 'A04.4']
        >>> df
        ICD10CM	ICD10CM_label	 ICD10CM_omop_id	SNOMED	  SNOMED_label	 SNOMED_omop_id
    0	A04.4	Other intestinal    35205417       111839008     192815      Intestinal
                Escherichia coli                                             infection due
                infections                                                   to E. coli
        """
        return self.target_table

    def save_source_to_target(self, filepath):
        """
        Save the source-to-target mapping table to a CSV file.

        Saves the merged table that maps concepts between the source
        and target vocabularies, and saves it as a CSV file to the specified
        filepath.

        Args:
            filepath: The filepath to save the source to target CSV file to.

        Examples:
        >>> vocab.save_source_to_target('folder/subfolder/out.csv')
        """
        self.target_table.to_csv(filepath, index = False)

    def save_source_to_target_failed_mappings(self, filepath):
        """
        Save the failed source to target mappings to a CSV file.

        Saves a pd.DataFrame that lists concepts that could not be matched
        between the source and target vocabularies to the specified
        filepath.

        Args:
            filepath: The filepath to save the failed mappings CSV file to.

        Examples:
        >>> vocab.save_source_to_target_failed_mappings('folder/subfolder/out.csv')
        >>> failed_mappings= pd.read_csv('folder/subfolder/out.csv')
        >>> failed_mappings
        ICD10CM	ICD10CM_label	ICD10CM_omop_id	SNOMED	SNOMED_label  SNOMED_omop_id
    0	A04.7	    NaN	             NaN	      NaN	    NaN	           NaN
        """
        failed_mappings = self.target_table[self.target_table[f'{self.target_vocab_value}_omop_id'].isnull()]
        failed_mappings.to_csv(filepath, index = False)
