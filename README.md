# InTAM Health Inc - EHR Database Repository

This repository contains the complete MySQL database schema for an Electronic Health Record (EHR) system designed for InTAM Health Inc.

## Overview

A comprehensive, production-ready database schema that supports all aspects of electronic medical records management, including:

- Patient demographics and insurance
- Clinical encounters and visits
- Medical history (past, family, social, surgical)
- Chief complaints and HPI
- Review of systems (ROS)
- Vital signs and physical examinations
- Physician orders (medications, labs, imaging, procedures)
- Laboratory results and imaging studies
- Diagnoses with ICD-10/ICD-11 codes
- Treatment plans and prescriptions
- Billing with CPT codes
- Nursing evaluations
- Patient tracking across departments
- Audit logging and compliance

## Files

- `generate_ehr_schema.py` - Python script to generate the complete MySQL schema
- `ehr_schema.sql` - Generated MySQL database schema (ready to execute)
- `EHR_SCHEMA_DOCUMENTATION.md` - Comprehensive documentation for the database schema

## Quick Start

### Generate the SQL Schema

```bash
python3 generate_ehr_schema.py > ehr_schema.sql
```

### Execute the Schema

```bash
# Option 1: From command line
mysql -u root -p < ehr_schema.sql

# Option 2: From MySQL prompt
mysql> source ehr_schema.sql;
```

## Database Features

### 40+ Tables covering:
- Patient Demographics
- Encounters and Visits
- Clinical Documentation
- Orders and Results
- Billing and Insurance
- Audit and Compliance

### Built-in Views
- Complete patient demographics
- Active encounters
- Patient allergies
- Active prescriptions
- Latest vital signs
- Patient tracker summary

### Stored Procedures
- Create new encounters
- Retrieve patient history
- Update patient ages

### Automated Features
- Auto-calculate BMI from height/weight
- Auto-update patient age from DOB
- Audit logging for all changes

## Documentation

For detailed documentation, see [EHR_SCHEMA_DOCUMENTATION.md](./EHR_SCHEMA_DOCUMENTATION.md)

## Requirements

- MySQL 5.7+ or MySQL 8.0+
- Python 3.6+ (for schema generation)

## License

Copyright InTAM Health Inc. All rights reserved.
