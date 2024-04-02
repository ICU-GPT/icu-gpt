# **icu-gpt**
## A gpt agent for icu databases analysis

## How to install icu-gpt 
#### Use PIP install icu-gpt

```bash
pip install https://github.com/ICU-GPT/icu-gpt.git
```
#### Use Soure code install icu-gpt
```bash
 git clone https://github.com/ICU-GPT/icu-gpt
 cd icu-gpt
 pip install .  ## or python steup.py install
```
## **How to use icu-gpt** 
##
>**You must prepare openai key and mimic related database account password**
 You can store them in **.env**
### prepare
**.env**  
```bash
OPENAI_API_KEY="sk-**" # you openai api key
PG_USER = 'mimic' # you  database username
PG_PASSWD = 'postgres' # you database password
PG_SERVER = '127.0.0.1' # you database ip address
```
### when you import icu-gpt env file will auto import


### Initialize llm-config use for Initialize openai client

```python
from autogen.oai import config_list_from_models
# build the gpt_configuration object
# Base Configuration
base_config = {
    "temperature": 0,
    "config_list": config_list_from_models(model_list=["gpt-4"]),
}

```

### Initialize database connect use for connect icu  database 

```python
from icu.db import db_conn

db,conn = db_conn() ## db is a SQLDatabase use for Query table structure and table information  conn obly a sqlalchemy engine

```
### Initialize icu-gpt to gen sql
```python
import icugpt
ag = icugpt.ICU(conn,llm_config=base_config) ## icu agent
ag.sql_chat(prompt='诊断为brain injury且年龄大于16的 入住icu 病人所有基础信息',tables=["mimiciv_icu.icustays","mimiciv_hosp.admissions","mimiciv_hosp.diagnoses_icd","mimiciv_hosp.d_icd_diagnoses", "mimiciv_hosp.patients","mimiciv_derived.icp"]) ## Start sql generation

```
###  
> **generation process**

```bash
ICUagent (to chat_manager):

You are a PostgreSQL expert. Given an input question, Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
Pay attention to use CURRENT_DATE function to get the current date, if the question involves "today".

Use the following format:
Question: Question here
SQLQuery: SQL Query to run
Only use the following tables:

CREATE TABLE mimiciv_derived.icp (
	subject_id INTEGER, 
	stay_id INTEGER, 
	charttime TIMESTAMP WITHOUT TIME ZONE, 
	icp DOUBLE PRECISION
)

/*
3 rows from icp table:
subject_id	stay_id	charttime	icp
10025463	38275267	2137-10-09 02:54:00	36.0
10025463	38275267	2137-10-09 03:15:00	11.0
10025463	38275267	2137-10-09 04:00:00	11.0
*/


CREATE TABLE mimiciv_hosp.d_icd_diagnoses (
	icd_code CHAR(7) NOT NULL, 
	icd_version SMALLINT NOT NULL, 
	long_title VARCHAR(255), 
	CONSTRAINT d_icd_diagnoses_pk PRIMARY KEY (icd_code, icd_version)
)

/*
3 rows from d_icd_diagnoses table:
icd_code	icd_version	long_title
0010   	9	Cholera due to vibrio cholerae
0011   	9	Cholera due to vibrio cholerae el tor
0019   	9	Cholera, unspecified
*/


CREATE TABLE mimiciv_hosp.patients (
	subject_id INTEGER NOT NULL, 
	gender CHAR(1) NOT NULL, 
	anchor_age SMALLINT, 
	anchor_year SMALLINT NOT NULL, 
	anchor_year_group VARCHAR(20) NOT NULL, 
	dod DATE, 
	CONSTRAINT patients_pk PRIMARY KEY (subject_id)
)

/*
3 rows from patients table:
subject_id	gender	anchor_age	anchor_year	anchor_year_group	dod
10000032	F	52	2180	2014 - 2016	2180-09-09
10000048	F	23	2126	2008 - 2010	None
10000068	F	19	2160	2008 - 2010	None
*/


CREATE TABLE mimiciv_hosp.admissions (
	subject_id INTEGER NOT NULL, 
	hadm_id INTEGER NOT NULL, 
	admittime TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	dischtime TIMESTAMP WITHOUT TIME ZONE, 
	deathtime TIMESTAMP WITHOUT TIME ZONE, 
	admission_type VARCHAR(40) NOT NULL, 
	admit_provider_id VARCHAR(10), 
	admission_location VARCHAR(60), 
	discharge_location VARCHAR(60), 
	insurance VARCHAR(255), 
	language VARCHAR(10), 
	marital_status VARCHAR(30), 
	race VARCHAR(80), 
	edregtime TIMESTAMP WITHOUT TIME ZONE, 
	edouttime TIMESTAMP WITHOUT TIME ZONE, 
	hospital_expire_flag SMALLINT, 
	CONSTRAINT admissions_pk PRIMARY KEY (hadm_id), 
	CONSTRAINT admissions_patients_fk FOREIGN KEY(subject_id) REFERENCES mimiciv_hosp.patients (subject_id)
)

/*
3 rows from admissions table:
subject_id	hadm_id	admittime	dischtime	deathtime	admission_type	admit_provider_id	admission_location	discharge_location	insurance	language	marital_status	race	edregtime	edouttime	hospital_expire_flag
10000032	22595853	2180-05-06 22:23:00	2180-05-07 17:15:00	None	URGENT	P874LG	TRANSFER FROM HOSPITAL	HOME	Other	ENGLISH	WIDOWED	WHITE	2180-05-06 19:17:00	2180-05-06 23:30:00	0
10000032	22841357	2180-06-26 18:27:00	2180-06-27 18:49:00	None	EW EMER.	P09Q6Y	EMERGENCY ROOM	HOME	Medicaid	ENGLISH	WIDOWED	WHITE	2180-06-26 15:54:00	2180-06-26 21:31:00	0
10000032	25742920	2180-08-05 23:44:00	2180-08-07 17:50:00	None	EW EMER.	P60CC5	EMERGENCY ROOM	HOSPICE	Medicaid	ENGLISH	WIDOWED	WHITE	2180-08-05 20:58:00	2180-08-06 01:44:00	0
*/


CREATE TABLE mimiciv_hosp.diagnoses_icd (
	subject_id INTEGER NOT NULL, 
	hadm_id INTEGER NOT NULL, 
	seq_num INTEGER NOT NULL, 
	icd_code CHAR(7) NOT NULL, 
	icd_version SMALLINT NOT NULL, 
	CONSTRAINT diagnoses_icd_pk PRIMARY KEY (hadm_id, seq_num, icd_code, icd_version), 
	CONSTRAINT diagnoses_icd_admissions_fk FOREIGN KEY(hadm_id) REFERENCES mimiciv_hosp.admissions (hadm_id), 
	CONSTRAINT diagnoses_icd_patients_fk FOREIGN KEY(subject_id) REFERENCES mimiciv_hosp.patients (subject_id)
)

/*
3 rows from diagnoses_icd table:
subject_id	hadm_id	seq_num	icd_code	icd_version
10000032	22595853	1	5723   	9
10000032	22595853	2	78959  	9
10000032	22595853	3	5715   	9
*/


CREATE TABLE mimiciv_icu.icustays (
	subject_id INTEGER NOT NULL, 
	hadm_id INTEGER NOT NULL, 
	stay_id INTEGER NOT NULL, 
	first_careunit VARCHAR(255), 
	last_careunit VARCHAR(255), 
	intime TIMESTAMP WITHOUT TIME ZONE, 
	outtime TIMESTAMP WITHOUT TIME ZONE, 
	los DOUBLE PRECISION, 
	CONSTRAINT icustays_pk PRIMARY KEY (stay_id), 
	CONSTRAINT icustays_admissions_fk FOREIGN KEY(hadm_id) REFERENCES mimiciv_hosp.admissions (hadm_id), 
	CONSTRAINT icustays_patients_fk FOREIGN KEY(subject_id) REFERENCES mimiciv_hosp.patients (subject_id)
)

/*
3 rows from icustays table:
subject_id	hadm_id	stay_id	first_careunit	last_careunit	intime	outtime	los
10000032	29079034	39553978	Medical Intensive Care Unit (MICU)	Medical Intensive Care Unit (MICU)	2180-07-23 14:00:00	2180-07-23 23:50:47	0.4102662037037037
10000980	26913865	39765666	Medical Intensive Care Unit (MICU)	Medical Intensive Care Unit (MICU)	2189-06-27 08:42:00	2189-06-27 20:38:27	0.4975347222222222
10001217	24597018	37067082	Surgical Intensive Care Unit (SICU)	Surgical Intensive Care Unit (SICU)	2157-11-20 19:18:02	2157-11-21 22:08:00	1.1180324074074075
*/

Question: 诊断为brain injury且年龄大于16的 入住icu 病人所有基础信息

--------------------------------------------------------------------------------
sql-agent (to chat_manager):

SQLQuery: 
SELECT 
    "patients"."subject_id", 
    "patients"."gender", 
    "patients"."anchor_age", 
    "patients"."anchor_year", 
    "patients"."anchor_year_group", 
    "patients"."dod", 
    "admissions"."hadm_id", 
    "admissions"."admittime", 
    "admissions"."dischtime", 
    "admissions"."deathtime", 
    "admissions"."admission_type", 
    "admissions"."admit_provider_id", 
    "admissions"."admission_location", 
    "admissions"."discharge_location", 
    "admissions"."insurance", 
    "admissions"."language", 
    "admissions"."marital_status", 
    "admissions"."race", 
    "admissions"."edregtime", 
    "admissions"."edouttime", 
    "admissions"."hospital_expire_flag", 
    "icustays"."stay_id", 
    "icustays"."first_careunit", 
    "icustays"."last_careunit", 
    "icustays"."intime", 
    "icustays"."outtime", 
    "icustays"."los"
FROM 
    "mimiciv_hosp"."patients" 
JOIN 
    "mimiciv_hosp"."admissions" ON "patients"."subject_id" = "admissions"."subject_id" 
JOIN 
    "mimiciv_icu"."icustays" ON "patients"."subject_id" = "icustays"."subject_id" 
JOIN 
    "mimiciv_hosp"."diagnoses_icd" ON "patients"."subject_id" = "diagnoses_icd"."subject_id" 
JOIN 
    "mimiciv_hosp"."d_icd_diagnoses" ON "diagnoses_icd"."icd_code" = "d_icd_diagnoses"."icd_code" 
WHERE 
    "d_icd_diagnoses"."long_title" LIKE '%brain injury%' 
    AND "patients"."anchor_age" > 16

--------------------------------------------------------------------------------
expert_agent (to chat_manager):

APPROVED

--------------------------------------------------------------------------------
ICUagent (to chat_manager):

You are a PostgreSQL expert. Given an input question, Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
Pay attention to use CURRENT_DATE function to get the current date, if the question involves "today".

Use the following format:
Question: Question here
SQLQuery: SQL Query to run
Only use the following tables:

CREATE TABLE mimiciv_derived.icp (
	subject_id INTEGER, 
	stay_id INTEGER, 
	charttime TIMESTAMP WITHOUT TIME ZONE, 
	icp DOUBLE PRECISION
)

/*
3 rows from icp table:
subject_id	stay_id	charttime	icp
10025463	38275267	2137-10-09 02:54:00	36.0
10025463	38275267	2137-10-09 03:15:00	11.0
10025463	38275267	2137-10-09 04:00:00	11.0
*/


CREATE TABLE mimiciv_hosp.d_icd_diagnoses (
	icd_code CHAR(7) NOT NULL, 
	icd_version SMALLINT NOT NULL, 
	long_title VARCHAR(255), 
	CONSTRAINT d_icd_diagnoses_pk PRIMARY KEY (icd_code, icd_version)
)

/*
3 rows from d_icd_diagnoses table:
icd_code	icd_version	long_title
0010   	9	Cholera due to vibrio cholerae
0011   	9	Cholera due to vibrio cholerae el tor
0019   	9	Cholera, unspecified
*/


CREATE TABLE mimiciv_hosp.patients (
	subject_id INTEGER NOT NULL, 
	gender CHAR(1) NOT NULL, 
	anchor_age SMALLINT, 
	anchor_year SMALLINT NOT NULL, 
	anchor_year_group VARCHAR(20) NOT NULL, 
	dod DATE, 
	CONSTRAINT patients_pk PRIMARY KEY (subject_id)
)

/*
3 rows from patients table:
subject_id	gender	anchor_age	anchor_year	anchor_year_group	dod
10000032	F	52	2180	2014 - 2016	2180-09-09
10000048	F	23	2126	2008 - 2010	None
10000068	F	19	2160	2008 - 2010	None
*/


CREATE TABLE mimiciv_hosp.admissions (
	subject_id INTEGER NOT NULL, 
	hadm_id INTEGER NOT NULL, 
	admittime TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	dischtime TIMESTAMP WITHOUT TIME ZONE, 
	deathtime TIMESTAMP WITHOUT TIME ZONE, 
	admission_type VARCHAR(40) NOT NULL, 
	admit_provider_id VARCHAR(10), 
	admission_location VARCHAR(60), 
	discharge_location VARCHAR(60), 
	insurance VARCHAR(255), 
	language VARCHAR(10), 
	marital_status VARCHAR(30), 
	race VARCHAR(80), 
	edregtime TIMESTAMP WITHOUT TIME ZONE, 
	edouttime TIMESTAMP WITHOUT TIME ZONE, 
	hospital_expire_flag SMALLINT, 
	CONSTRAINT admissions_pk PRIMARY KEY (hadm_id), 
	CONSTRAINT admissions_patients_fk FOREIGN KEY(subject_id) REFERENCES mimiciv_hosp.patients (subject_id)
)

/*
3 rows from admissions table:
subject_id	hadm_id	admittime	dischtime	deathtime	admission_type	admit_provider_id	admission_location	discharge_location	insurance	language	marital_status	race	edregtime	edouttime	hospital_expire_flag
10000032	22595853	2180-05-06 22:23:00	2180-05-07 17:15:00	None	URGENT	P874LG	TRANSFER FROM HOSPITAL	HOME	Other	ENGLISH	WIDOWED	WHITE	2180-05-06 19:17:00	2180-05-06 23:30:00	0
10000032	22841357	2180-06-26 18:27:00	2180-06-27 18:49:00	None	EW EMER.	P09Q6Y	EMERGENCY ROOM	HOME	Medicaid	ENGLISH	WIDOWED	WHITE	2180-06-26 15:54:00	2180-06-26 21:31:00	0
10000032	25742920	2180-08-05 23:44:00	2180-08-07 17:50:00	None	EW EMER.	P60CC5	EMERGENCY ROOM	HOSPICE	Medicaid	ENGLISH	WIDOWED	WHITE	2180-08-05 20:58:00	2180-08-06 01:44:00	0
*/


CREATE TABLE mimiciv_hosp.diagnoses_icd (
	subject_id INTEGER NOT NULL, 
	hadm_id INTEGER NOT NULL, 
	seq_num INTEGER NOT NULL, 
	icd_code CHAR(7) NOT NULL, 
	icd_version SMALLINT NOT NULL, 
	CONSTRAINT diagnoses_icd_pk PRIMARY KEY (hadm_id, seq_num, icd_code, icd_version), 
	CONSTRAINT diagnoses_icd_admissions_fk FOREIGN KEY(hadm_id) REFERENCES mimiciv_hosp.admissions (hadm_id), 
	CONSTRAINT diagnoses_icd_patients_fk FOREIGN KEY(subject_id) REFERENCES mimiciv_hosp.patients (subject_id)
)

/*
3 rows from diagnoses_icd table:
subject_id	hadm_id	seq_num	icd_code	icd_version
10000032	22595853	1	5723   	9
10000032	22595853	2	78959  	9
10000032	22595853	3	5715   	9
*/


CREATE TABLE mimiciv_icu.icustays (
	subject_id INTEGER NOT NULL, 
	hadm_id INTEGER NOT NULL, 
	stay_id INTEGER NOT NULL, 
	first_careunit VARCHAR(255), 
	last_careunit VARCHAR(255), 
	intime TIMESTAMP WITHOUT TIME ZONE, 
	outtime TIMESTAMP WITHOUT TIME ZONE, 
	los DOUBLE PRECISION, 
	CONSTRAINT icustays_pk PRIMARY KEY (stay_id), 
	CONSTRAINT icustays_admissions_fk FOREIGN KEY(hadm_id) REFERENCES mimiciv_hosp.admissions (hadm_id), 
	CONSTRAINT icustays_patients_fk FOREIGN KEY(subject_id) REFERENCES mimiciv_hosp.patients (subject_id)
)

/*
3 rows from icustays table:
subject_id	hadm_id	stay_id	first_careunit	last_careunit	intime	outtime	los
10000032	29079034	39553978	Medical Intensive Care Unit (MICU)	Medical Intensive Care Unit (MICU)	2180-07-23 14:00:00	2180-07-23 23:50:47	0.4102662037037037
10000980	26913865	39765666	Medical Intensive Care Unit (MICU)	Medical Intensive Care Unit (MICU)	2189-06-27 08:42:00	2189-06-27 20:38:27	0.4975347222222222
10001217	24597018	37067082	Surgical Intensive Care Unit (SICU)	Surgical Intensive Care Unit (SICU)	2157-11-20 19:18:02	2157-11-21 22:08:00	1.1180324074074075
*/

Question: 诊断为brain injury且年龄大于16的 入住icu 病人所有基础信息

--------------------------------------------------------------------------------
sql-agent (to chat_manager):

SQLQuery: 
SELECT 
    "patients"."subject_id", 
    "patients"."gender", 
    "patients"."anchor_age", 
    "patients"."anchor_year", 
    "patients"."anchor_year_group", 
    "patients"."dod", 
    "admissions"."hadm_id", 
    "admissions"."admittime", 
    "admissions"."dischtime", 
    "admissions"."deathtime", 
    "admissions"."admission_type", 
    "admissions"."admit_provider_id", 
    "admissions"."admission_location", 
    "admissions"."discharge_location", 
    "admissions"."insurance", 
    "admissions"."language", 
    "admissions"."marital_status", 
    "admissions"."race", 
    "admissions"."edregtime", 
    "admissions"."edouttime", 
    "admissions"."hospital_expire_flag", 
    "icustays"."stay_id", 
    "icustays"."first_careunit", 
    "icustays"."last_careunit", 
    "icustays"."intime", 
    "icustays"."outtime", 
    "icustays"."los"
FROM 
    "mimiciv_hosp"."patients" 
JOIN 
    "mimiciv_hosp"."admissions" ON "patients"."subject_id" = "admissions"."subject_id" 
JOIN 
    "mimiciv_icu"."icustays" ON "patients"."subject_id" = "icustays"."subject_id" 
JOIN 
    "mimiciv_hosp"."diagnoses_icd" ON "patients"."subject_id" = "diagnoses_icd"."subject_id" 
JOIN 
    "mimiciv_hosp"."d_icd_diagnoses" ON "diagnoses_icd"."icd_code" = "d_icd_diagnoses"."icd_code" 
WHERE 
    "d_icd_diagnoses"."long_title" LIKE '%brain injury%' 
    AND "patients"."anchor_age" > 16

--------------------------------------------------------------------------------
expert_agent (to chat_manager):

APPROVED

```
### Generate SQl behind the SQLQuery: 
```sql
SELECT 
    "patients"."subject_id", 
    "patients"."gender", 
    "patients"."anchor_age", 
    "patients"."anchor_year", 
    "patients"."anchor_year_group", 
    "patients"."dod", 
    "admissions"."hadm_id", 
    "admissions"."admittime", 
    "admissions"."dischtime", 
    "admissions"."deathtime", 
    "admissions"."admission_type", 
    "admissions"."admit_provider_id", 
    "admissions"."admission_location", 
    "admissions"."discharge_location", 
    "admissions"."insurance", 
    "admissions"."language", 
    "admissions"."marital_status", 
    "admissions"."race", 
    "admissions"."edregtime", 
    "admissions"."edouttime", 
    "admissions"."hospital_expire_flag", 
    "icustays"."stay_id", 
    "icustays"."first_careunit", 
    "icustays"."last_careunit", 
    "icustays"."intime", 
    "icustays"."outtime", 
    "icustays"."los"
FROM 
    "mimiciv_hosp"."patients" 
JOIN 
    "mimiciv_hosp"."admissions" ON "patients"."subject_id" = "admissions"."subject_id" 
JOIN 
    "mimiciv_icu"."icustays" ON "patients"."subject_id" = "icustays"."subject_id" 
JOIN 
    "mimiciv_hosp"."diagnoses_icd" ON "patients"."subject_id" = "diagnoses_icd"."subject_id" 
JOIN 
    "mimiciv_hosp"."d_icd_diagnoses" ON "diagnoses_icd"."icd_code" = "d_icd_diagnoses"."icd_code" 
WHERE 
    "d_icd_diagnoses"."long_title" LIKE '%brain injury%' 
    AND "patients"."anchor_age" > 16


```
