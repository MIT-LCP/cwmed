import pandas as pd


class Standard_vocab_translator(object):
    def __init__(self, source_vocabulary:str, target_vocabulary:str, source_file:str, source_file_code_column:str):
        # Vocabulary Variables
        self.source_vocabulary = source_vocabulary
        self.target_vocabulary = target_vocabulary
        
        # Concept dictionary load.
        concept=pd.read_csv("CONCEPT.csv",sep="\\t",error_bad_lines=False, 
                            converters={"concept_id":str,"concept_code":str}, engine='python')
        #List of all vocabularies in the diccionary
        self.vocab_list=concept["vocabulary_id"].unique()
        
        # Concept relationship dictionary load.
        concept_rel=pd.read_csv("CONCEPT_RELATIONSHIP.csv",sep="\\t",error_bad_lines=False, 
                        converters={"concept_id_1":str,"concept_id_2":str}, engine='python')
        
        
        # Select only the needed vocabularies. 
        
        # Example with 'NDC' and 'RxNorm'
        concept=concept[(concept["vocabulary_id"]==source_vocabulary)|(concept["vocabulary_id"]==target_vocabulary)]
        # Select only the relationships on "mapping to". 
        concept_rel=concept_rel[concept_rel['relationship_id']=="Maps to"]
        
        
        # Load your source file.
        source_voc=pd.read_csv(source_file,converters={source_file_code_column:str})
        
        #1 Translate your source vocabulary code(concept_name) TO concept_id(NDC).
        #replace left_on value for the source code columns name.
        concept_id_source=source_voc.merge(concept, how='left',left_on=source_file_code_column, right_on="concept_code")
        
        # 2 step. Merge tables joining on concept_id(from source voc) to concept_id()
        source_rel_merge=concept_id_source.merge(concept_rel, how='left',left_on="concept_id",right_on="concept_id_1")
        
        # Cleaning undesired columns 
        source_rel_merge=source_rel_merge[[source_file_code_column,'concept_id','concept_id_1','concept_id_2']]
        
        
        # step 3. Merge tables joining the concept_id_2(concept_id from target voc) with concept dictionary to 
        # obabstain the concept_code of the target voc.

        rel_target_merge = source_rel_merge.merge(concept, how='left',left_on="concept_id_2",right_on="concept_id")
        
        rel_target_merge=rel_target_merge[[source_file_code_column,'concept_id_x','concept_id_1','concept_id_2','concept_code']]
        # Renaming columns for clarity
        
        rel_target_merge.columns=[source_file_code_column,'concept_id_x','concept_id_{}'.format(source_vocabulary),
                                  'concept_id_{}'.format(target_vocabulary),target_vocabulary]
        
        self.rel_target_merge = rel_target_merge
        
    def print_dic(self):
        print(self.rel_target_merge)
    
    def save_dic(self,target_file):
        self.rel_target_merge.to_csv(target_file)
    
    def failed_mappings(self):
        failed_mappings = self.rel_target_merge[self.rel_target_merge['concept_id_{}'.format(self.source_vocabulary)].isnull()]
        failed_mappings.to_csv("failed_mappings.csv")
        
  
