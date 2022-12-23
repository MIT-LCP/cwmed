"""Crosswalk using the OMOP vocabulary files.

Module for walking between medical vocabularies (e.g. RxNorm, NDC). Uses
standardized vocabulary files downloaded from the OHDSI website:
https://www.ohdsi.org/analytic-tools/athena-standardized-vocabularies/
"""

import pandas as pd
import os
import requests
import zipfile
import io


def download_data():
    '''
    Downloads and unzips two required files
    (1) concept.csv and (2) concept_relationship.csv
    using the url link emailed to registered users on the athena website.
    '''
    url = input('url:')
    response = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(response.content))
    data_directory = os.getcwd()+'/data'
    z.extractall(data_directory, members=[i for i in z.namelist()
                 if i in ('CONCEPT.csv', 'CONCEPT_RELATIONSHIP.csv')])

def check_concept_file_source_target_values(concept_filepath):
    """Checks available source and target vocabulary values from Athena.
    """
    
    concepts = pd.read_csv(concept_filepath, sep='\t')

    # List all vocabularies in concept dictionary.
    unique_vocab_values = concepts["vocabulary_id"].unique()

    return unique_vocab_values

class VocabTranslator(object):
    """Merge tables to create a crosswalk between two vocabularies.

    Merge a source and target standardized vocabulary. The final merged table
    can then be outputted to a CSV. Requires vocabulary and concept
    relationship files downloaded from the OHDSI website.

    Args:
        source_filepath (str): Path to source vocabulary.
        source_code_col (str): Column in source vocabulary that will be mapped to the target vocabulary.
        concept_filepath (str): Path to concept.csv.
        source_vocab_value (str): Value of the source vocabulary.
        target_vocab_value (str): Value of target vocabulary.
        concept_relationship_filepath = Path to concept_relationship.csv.

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
        self.target_table = self._map_concept_id_2_to_concept_code()

    def _read_source_file(self):
        """Reads the source file.
        
        Returns a pd.DataFrame that includes the source code.
        """
        source_df = pd.read_csv(self.source_filepath,
                                 converters={self.source_code_col: str})
        return source_df

    def _read_concept_relationship_file(self):
        """ Loads a pairwise concept relationship dictionary that contains concept_id_1 and concept_id_2
        Returns a pd.DataFrame with the concept_id_1, concept_id_2 and relationship_id.
        """
        concept_relationship_df = pd.read_csv(self.concept_relationship_filepath, sep='\t',
                                               converters={"concept_id_1": str,
                                                           "concept_id_2": str})
        concept_relationship_df = concept_relationship_df[concept_relationship_df['relationship_id'] == "Maps to"]

        return concept_relationship_df

    def _read_concept_file(self):
        """Loads omop concept dictionary that contains concept_id (omop id),
           concept_code(common vocab code) and vocabulary_id (common vocab name)
           with the specified source and target values.

           Returns a pd.DataFrame with the concept_id, concept_code and vocabulary_id.
        """
        concept_df = pd.read_csv(self.concept_filepath, sep='\t',
                                  converters={"concept_id": str,
                                              "concept_code": str})

        # Select only the needed vocabularies, e.g. 'NDC' and 'RxNorm'.
        concept_df = concept_df[(concept_df["vocabulary_id"] == self.source_vocab_value) |
                                 (concept_df["vocabulary_id"] == self.target_vocab_value)]

        return concept_df

    def _map_source_code_to_concept_id (self):
        """
        Maps source code e.g. ndc to OMOP concept_id using concept_code e.g.ndc in the concept.csv.
        """
        source_code_to_concept_id_df = self._read_source_file().merge(self.concept_file, how='left',
                                    left_on=self.source_code_col, right_on="concept_code")

        return source_code_to_concept_id_df

    def _map_concept_id_to_concept_id_2 (self):
        """
        Maps concept_id in concept.csv to concept_id_2 using concept_id_1 in the concept_relationship.csv.
        """
        concept_id_to_concept_id_2_df = self._map_source_code_to_concept_id().merge(self._read_concept_relationship_file(),
                                                                                    how='left',
                                                                                    left_on="concept_id",
                                                                                    right_on="concept_id_1")
        # Select relevant columns from merge tables.
        concept_id_to_concept_id_2_df = concept_id_to_concept_id_2_df[[self.source_code_col,
                                                                            'concept_id',
                                                                            'concept_id_1',
                                                                            'concept_id_2']]
        return concept_id_to_concept_id_2_df

    def _map_concept_id_2_to_concept_code(self):
        """
        Maps concept_id_2 in the concept_relationship.csv to concept_code (target code)
        using concept_id in the concept.csv.
        """
        concept_id_2_to_concept_code_df = self._map_concept_id_to_concept_id_2().merge(self.concept_file, how='left',
                                                                                     left_on="concept_id_2",
                                                                                     right_on="concept_id")

        # Select relevant columns from merge tables.
        concept_id_2_to_concept_code_df = concept_id_2_to_concept_code_df[[self.source_code_col,
                                                                             'concept_id_x',
                                                                             'concept_id_1',
                                                                             'concept_id_2',
                                                                             'concept_code',
                                                                             'concept_name']]

        # Renaming columns for clarity
        concept_id_2_to_concept_code_df.columns = [self.source_code_col,
                                                     'concept_id_x',
                                                     'concept_id_{}'.format(self.target_vocab_value),
                                                     'concept_id_{}'.format(self.source_vocab_value),
                                                     self.target_vocab_value,
                                                     'concept_name']

        return concept_id_2_to_concept_code_df

    def print_dic(self):
        """Prints the merged table.

        Prints a pd.DataFrame that maps concepts between the source and target
        vocabularies.
        """
        print(self.target_table)

    def save_dic(self, target_file):
        """Saves the merged table to CSV.

        Saves a pd.DataFrame that maps concepts between the source and target
        vocabularies.
        """
        self.target_table.to_csv(target_file, index = False)

    def failed_mappings(self, target_failed_mappings_file):
        """Prints a table of failed mappings.

        Prints a pd.DataFrame that lists concepts that could not be matched
        between the source and target vocabularies.
        """
        failed_mappings = self.target_table[self.target_table[
            'concept_id_{}'.format(
                self.source_vocab_value)].isnull()]
        failed_mappings.to_csv(target_failed_mappings_file, index = False)
