# medical-standard-voc-translator


GIT_HUB_ENCICLOPEDIA Vocabularies:

VOCABULARIES COVERED:

ICD10CM	-	International Classification of Diseases, Tenth Revision, Clinical Modification (NCHS) <br>
LOINC	-	Logical Observation Identifiers Names and Codes (Regenstrief Institute)<br>
SNOMED	-	Systematic Nomenclature of Medicine - Clinical Terms (IHTSDO)<br>
NDC	-	National Drug Code (FDA and manufacturers)<br>
MDC	-	Major Diagnostic Categories (CMS)<br>
ICD10	-	International Classification of Diseases, Tenth Revision (WHO)<br>
RxNorm Extension	-	RxNorm Extension (OHDSI)<br>
RxNorm	-	RxNorm (NLM)<br>
ICD9Proc	-	International Classification of Diseases, Ninth Revision, Clinical Modification, Volume 3 (NCHS)<br>
ATC	-	WHO Anatomic Therapeutic Chemical Classification<br>
CPT4	-	Current Procedural Terminology version 4 (AMA)<br>
DRG	-	Diagnosis-related group (CMS)<br>
ICD9CM	-	International Classification of Diseases, Ninth Revision, Clinical Modification, Volume 1 and 2 (NCHS)<br>
OMOP Extension	-	OMOP Extension (OHDSI)<br>





Objective: The objective of this repository is to guide the translation from one standard vocabulary to another standard vocabulary through OMOP vocabulary resources.

FILES REQUIRED: Register, log in and select the desired  vocabulary source and target from [Athena](https://athena.ohdsi.org/vocabulary/list)


The Athena web app will send a link to download a ZIP file that will include the next files:

CONCEPT.csv: Contains the relation between concept_code and concept_id.
CONCEPT_RELATIONSHIP.csv: This contains the relationship between the concept_id.
This files are dictionaries that need to be stored in the same folder as the pyhton notebook. 


Glossary:
concept_code: code from the source vocabulary that represents one concept.
concept_id: code from OMOP that represents one concept.

OMOP :

Every concept_code has its concept_id. The concept_code does not converge to a concept_id: For the same concept(amoxicillin 250mg Oral Capsule), there will be different OMOP codes (one for each vocabulary) and different concept_id. Those  concept_id(s) are related in the dictionary concept_relationship.


Example:
We want to translate [amoxicillin 250 MG Oral Capsule] from RxNorm code to NDC code.

Step 1:
Translate the source code to the omop code.
CONCEPT_CODE(SOURCE CODE)--  CONCEPT  --> CONCEPT_ID(OMOP CODE)


 
| VOCAB | concept_code (RX NORM) | concept_id |
| -------- | ------------ | ------- |
| RX NORM | 308182      | 19073183 |


Step 2:
Use the concept_relationship dictionary to relate concept_id just obtained from step 1 that maps to other different concept_id .


CONCEPT_ID_1(OMOP CODE FROM SOURCE VOCAB) --> CONCEPT_RELATIONSHIP --> CONCEPT_ID_2(OMOP CODE FROM TARGET VOCAB)

source concept_id is concept_id_1 and target concept_id is concept_id_2

| concept_id_1 | concept_id_2 |
| --------- | ---------- |
| 19073183  | 44420386 |


Step 3:

Use the new concept_id_2  to obtain the concept_code of the target vocabulary 

CONCEPT_ID_2(OMOP CODE FROM TARGET VOCAB) -->CONCEPT--> CONCEPT_CODE(TARGET CODE)

| VOCAB | concept_id| concept_code (NDC) | 
| -------- | ------------ | ------- |
| NDC     | 44420386 | 43858035231 | 


