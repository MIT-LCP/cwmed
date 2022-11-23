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

        # Concept relationship dictionary load.
        concept_rel = pd.read_csv(
            self.concept_relationship_filepath, sep="\\t",
            error_bad_lines=False,
            converters={"concept_id_1": str,
                        "concept_id_2": str}, engine='python')

        # Select only the relationships on "mapping to".
        concept_rel = concept_rel[concept_rel['relationship_id'] == "Maps to"]

        # 1 Translate your source vocabulary code(concept_name) TO
        # concept_id(NDC).
        # replace left_on value for the source code columns name.
        concept_id_source = self.__read_source_file().merge(
            self.__read_concept_file, how='left',
            left_on=self.source_code_col, right_on="concept_code")

        # 2 step. Merge tables joining on concept_id(from source voc) to
        #  concept_id()
        source_rel_merge = concept_id_source.merge(
            concept_rel, how='left',
            left_on="concept_id",
            right_on="concept_id_1")

        # Cleaning undesired columns
        source_rel_merge = source_rel_merge[[self.source_code_col,
                                             'concept_id',
                                             'concept_id_1',
                                             'concept_id_2']]

        # step 3. Merge tables joining the concept_id_2(concept_id from target
        # voc) with concept dictionary to
        # obabstain the concept_code of the target voc.

        rel_target_merge = source_rel_merge.merge(
            self.__read_concept_file(), how='left',
            left_on="concept_id_2",
            right_on="concept_id")

        rel_target_merge = rel_target_merge[[
            self.source_code_col,
            'concept_id_x',
            'concept_id_1',
            'concept_id_2',
            'concept_code',
            'concept_name']]
        # Renaming columns for clarity

        rel_target_merge.columns = [
            self.source_code_col,
            'concept_id_x',
            'concept_id_{}'.format(self.source_vocab_value),
            'concept_id_{}'.format(self.target_vocab_value),
            self.target_vocab_value,
            'concept_name_{}'.format(self.target_vocab_value)]


        self.rel_target_merge = rel_target_merge
    
    def __read_source_file(self):
        """Reads the source file.
        
        Returns a pd.DataFrame that includes the source code.
        """
        source_df = pd.read_csv(self.source_filepath,
                                 converters={self.source_code_col: str})
        return source_df

    def __read_concept_file(self):
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

    def print_dic(self):
        """Prints the merged table.

        Prints a pd.DataFrame that maps concepts between the source and target
        vocabularies.
        """
        print(self.rel_target_merge)

    def save_dic(self, target_file):
        """Saves the merged table to CSV.

        Saves a pd.DataFrame that maps concepts between the source and target
        vocabularies.
        """
        self.rel_target_merge.to_csv(target_file)

    def failed_mappings(self):
        """Prints a table of failed mappings.

        Prints a pd.DataFrame that lists concepts that could not be matched
        between the source and target vocabularies.
        """
        failed_mappings = self.rel_target_merge[self.rel_target_merge[
            'concept_id_{}'.format(
                self.source_vocab_value)].isnull()]
        failed_mappings.to_csv("failed_mappings.csv")
