# medical-standard-voc-translator



GIT_HUB_ENCICLOPEDIA Vocabularies:

VOCABULARIES COVERED:

ICD10CM	-	International Classification of Diseases, Tenth Revision, Clinical Modification (NCHS)
LOINC	-	Logical Observation Identifiers Names and Codes (Regenstrief Institute)
SNOMED	-	Systematic Nomenclature of Medicine - Clinical Terms (IHTSDO)
NDC	-	National Drug Code (FDA and manufacturers)
MDC	-	Major Diagnostic Categories (CMS)
ICD10	-	International Classification of Diseases, Tenth Revision (WHO)
RxNorm Extension	-	RxNorm Extension (OHDSI)
RxNorm	-	RxNorm (NLM)
ICD9Proc	-	International Classification of Diseases, Ninth Revision, Clinical Modification, Volume 3 (NCHS)
ATC	-	WHO Anatomic Therapeutic Chemical Classification
CPT4	-	Current Procedural Terminology version 4 (AMA)
DRG	-	Diagnosis-related group (CMS)
ICD9CM	-	International Classification of Diseases, Ninth Revision, Clinical Modification, Volume 1 and 2 (NCHS)
OMOP Extension	-	OMOP Extension (OHDSI)




Step 1
CONCEPT_CODE(SOURCE CODE)--  CONCEPT_DIC  --> CONCEPT_ID(OMOP CODE)

Step 2
CONCEPT_ID_1(OMOP CODE FROM SOURCE VOCAB) --> CONCEPT_RELATIONSHIP --> CONCEPT_ID_2(OMOP CODE FROM TARGET VOCAB)

Step 3
CONCEPT_ID_2(OMOP CODE FROM TARGET VOCAB) -->CONCEPT_DIC--> CONCEPT_CODE(TARGET CODE)


Objective: To translate from one standard vocabulary to another standard vocabulary through OMOP vocabulary resources.


Dictionaries:

CONCEPT_DIC: Contains the relation between concept_code and concept_id.

CONCEPT_RELATIONSHIP: Contains the relationship between the concept_id.



Method:

Every concept_code has their conept_id.
They are not crossed: For the same concept(amoxicillin 250mg Oral Capsule) two different codes (one for each vocabulary) are related to two different concept_id(omop code).

Example:
amoxicillin 250 MG Oral Capsule :  
|--------|-------------------------|---------------------|
|RX NORM |Concept_code 308182      |Concept_ID  19073183 |
|NDC     |Concept code 43858035231 |Concept_ID  44420386 |



