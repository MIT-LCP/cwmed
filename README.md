# Crosswalk Medical

## Introduction

Crosswalk medical faciliates the conversion of clinical terminology between two different coding systems. This enables seemless data exchange, integration and interoperability between different healthcare information systems, overcoming barries imposed by disparate coding systems.

## Documentation and Usage

Crosswalk medical is a Python package to assist the semantic interoperability when federating clinical databases. The objective of the package is to guide the crosswalk from one standard source vocabulary to a target vocabulary by defining concepts and utilizing semantic relationships avaliable via downloadable source and target dictionaries on [Athena](https://athena.ohdsi.org/vocabulary/list) that capture associations between two different concepts.

See [Downloading Source and Target Vocabularies](#download-vocabs) section for downloading source and target vocabularies.

See [Installation](#install) section for package installation.

See [demo.ipynb](https://github.com/xborrat/medical-standard-voc-translator/blob/main/example_crosswalk.ipynb) notebook file for example use cases.

## <a id="install"></a>Installation

The distribution is hosted on PyPI at: https://pypi.org/project/cwmed/0.1.0/. The package can be directly installed from PyPI using pip:

```sh
pip install cwmed
```

## <a id="download-vocabs"></a>Downloading Source and Target Vocabularies

Register on [Athena](https://athena.ohdsi.org/vocabulary/list), log in, and select the desired source and target vocabularies for download.

A link will be sent to your registered email to enable the download of a ZIP file that will include these dependencies:

CONCEPT.csv: This dictionary contains the relation between concept_code and concept_id.<br>
CONCEPT_RELATIONSHIP.csv: This dictionary contains the relationships between the different `concept_id(s). We will use the "Maps to" type of relation to translate codes between dictionaries.
These files are dictionaries that need to be stored in the same folder as the python notebook. 

Few examaples of downloadable vocabularies avaliable on Athena:

LOINC	-	Logical Observation Identifiers Names and Codes (Regenstrief Institute)<br>
SNOMED	-	Systematic Nomenclature of Medicine - Clinical Terms (IHTSDO)<br>
NDC	-	National Drug Code (FDA and manufacturers)<br>
RxNorm Extension	-	RxNorm Extension (OHDSI)<br>
RxNorm	-	RxNorm (NLM)<br>
ICD10CM	-	International Classification of Diseases, Tenth Revision, Clinical Modification (NCHS) <br>
ICD9CM	-	International Classification of Diseases, Ninth Revision, Clinical Modification, Volume 1 and 2 (NCHS)<br>
ICD9Proc	-	International Classification of Diseases, Ninth Revision, Clinical Modification, Volume 3 (NCHS)<br>
CPT4	-	Current Procedural Terminology version 4 (AMA)<br>
OMOP Extension	-	OMOP Extension (OHDSI)<br>

### Crosswalk Medical Recipe

Definitions:
`concept_code`: code from the source vocabulary that represents one concept. 
Example: For the concept  (0.5 ML Fondaparinux sodium 5 MG/ML Prefilled Syringe [Arixtra] the concept_code for NDC is: 00007323001
`concept_id`: code from [OMOP](https://www.ohdsi.org/data-standardization/) that corresponds to a concept_code. 
Example: For concept (0.5 ML Fondaparinux sodium 5 MG/ML Prefilled Syringe [Arixtra] the concept_id corresponding to concept_code 00007323001 is 44838028.

Every concept_code has a related `concept_id`. The `concept_code` does not converge to a `concept_id`: For the same concept(amoxicillin 250mg Oral Capsule), there will be different OMOP codes(concept_id) one for each vocabulary. Those  `concept_id`(s) are related in the dictionary concept_relationship.
|DRUG | VOCAB | concept_code  | concept_id |
 |-------------------------------| -------- | ------------ | ------- |
amoxicillin 250 MG Oral Capsule | RX NORM | 308182      | 19073183 |
 amoxicillin 250 MG Oral Capsule| NDC     | 44420386 | 43858035231 | 
 
 Every `concept_code` has a different `concept_id` even though they represent the same concept in the real world. In the above table, the same drug has two different `concept_code`s for each vocabulary and also a different `concept_id`.


### Use Case

Use Case: Translate [amoxicillin 250 MG Oral Capsule] from RxNorm code to NDC code.

Step 1:
Translate the source code to the OMOP code.
CONCEPT_CODE(SOURCE CODE)--  CONCEPT  --> CONCEPT_ID(OMOP CODE)


| VOCAB | concept_code (RX NORM) | concept_id |
| -------- | ------------ | ------- |
| RX NORM | 308182      | 19073183 |

Step 2:
Use the concept_relationship dictionary to relate the `concept_id` obtained from step 1 and map it to the target vocabulary `concept_id` .

CONCEPT_ID_1(OMOP CODE FROM SOURCE VOCAB) --> CONCEPT_RELATIONSHIP --> CONCEPT_ID_2(OMOP CODE FROM TARGET VOCAB)

source concept_id is concept_id_1 and target concept_id is concept_id_2

| concept_id_1 | concept_id_2 |
| --------- | ---------- |
| 19073183  | 44420386 |

Step 3:
Use the new concept_id_2  to obtain the `concept_code` of the target vocabulary. 

CONCEPT_ID_2(OMOP CODE FROM TARGET VOCAB) -->CONCEPT--> CONCEPT_CODE(TARGET CODE)

| VOCAB | concept_id| concept_code (NDC) | 
| -------- | ------------ | ------- |
| NDC     | 44420386 | 43858035231 | 
