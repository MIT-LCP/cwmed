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
        source_vocabulary (str): Filename of the source vocabulary.
        target_vocabulary (str): Filename of the target vocabulary.
        source_file (str): Path to the source vocabulary.
        source_file_code_column (str): Column in source vocabulary that will
            be mapped to the target vocabulary.

    Attributes:
        source_vocabulary (str): Filename of the source vocabulary.
        target_vocabulary (str): Filename of the target vocabulary.
        vocab_list (pd.DataFrame): List of unique concept IDs in the
            concept.csv file.
        source_voc (pd.DataFrame): Source vocabulary file loaded from CSV.
        rel_target_merge (pd.DataFrame): Merged table of the source and target.

    """

    def __init__(self, source_vocabulary: str, target_vocabulary: str,
                 source_file: str, source_file_code_column: str, concept_file: str, concept_relationship_file: str):
        # Vocabulary Variables
        self.source_vocabulary = source_vocabulary
        self.target_vocabulary = target_vocabulary
        # Concept dictionary load.
        concept = pd.read_csv(concept_file, sep="\\t", error_bad_lines=False,
                              converters={"concept_id": str,
                                          "concept_code": str},
                              engine='python')
        # List of all vocabularies in the diccionary
        self.vocab_list = concept["vocabulary_id"].unique()

        # Concept relationship dictionary load.
        concept_rel = pd.read_csv(
            concept_relationship_file, sep="\\t",
            error_bad_lines=False,
            converters={"concept_id_1": str,
                        "concept_id_2": str}, engine='python')

        # Select only the needed vocabularies.

        # Example with 'NDC' and 'RxNorm'
        concept = concept[(concept["vocabulary_id"] == source_vocabulary)
                          | (concept["vocabulary_id"] == target_vocabulary)]

        # Select only the relationships on "mapping to".
        concept_rel = concept_rel[concept_rel['relationship_id'] == "Maps to"]

        # Load your source file.
        source_voc = pd.read_csv(source_file,
                                 converters={source_file_code_column: str})
        self.source_voc = source_voc

        # 1 Translate your source vocabulary code(concept_name) TO
        # concept_id(NDC).
        # replace left_on value for the source code columns name.
        concept_id_source = source_voc.merge(
            concept, how='left',
            left_on=source_file_code_column, right_on="concept_code")

        # 2 step. Merge tables joining on concept_id(from source voc) to
        #  concept_id()
        source_rel_merge = concept_id_source.merge(
            concept_rel, how='left',
            left_on="concept_id",
            right_on="concept_id_1")

        # Cleaning undesired columns
        source_rel_merge = source_rel_merge[[source_file_code_column,
                                             'concept_id',
                                             'concept_id_1',
                                             'concept_id_2']]

        # step 3. Merge tables joining the concept_id_2(concept_id from target
        # voc) with concept dictionary to
        # obabstain the concept_code of the target voc.

        rel_target_merge = source_rel_merge.merge(
            concept, how='left',
            left_on="concept_id_2",
            right_on="concept_id")

        rel_target_merge = rel_target_merge[[
            source_file_code_column,
            'concept_id_x',
            'concept_id_1',
            'concept_id_2',
            'concept_code']]
        # Renaming columns for clarity

        rel_target_merge.columns = [
            source_file_code_column,
            'concept_id_x',
            'concept_id_{}'.format(source_vocabulary),
            'concept_id_{}'.format(target_vocabulary),
            target_vocabulary]

        self.rel_target_merge = rel_target_merge

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
                self.source_vocabulary)].isnull()]
        failed_mappings.to_csv("failed_mappings.csv")
