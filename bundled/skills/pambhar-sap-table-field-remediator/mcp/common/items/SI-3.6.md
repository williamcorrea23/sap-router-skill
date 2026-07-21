---
item_id: SI-3.6
title: "3.6 S4TWL - Deprecation of 4 fields from FSBP table BP1010"
pages: 132-135
sap_notes: [1000009, 1765305, 3216733, 3327581]
components: [FS-BP]
objects: []
---
Application Components:FS-BP

Related Notes:

| Note Type       |   Note Number | Note Description                                                                                                  |
|-----------------|---------------|-------------------------------------------------------------------------------------------------------------------|
| Business Impact |       3216733 | S4TWL - Rating fields of table BP1010 (Creditworthiness Data) of FSBP enhancement to SAP BP) will become obsolete |

## Symptom

You execute a system conversion from ERP to S/4HANA or an upgrade from a lower S/4HANA release to a higher one (higher than 2023 - in S4/HANA 2023 the functionality will still be available).

The four fields SOL_INS (Institute Providing Credit Standing Information), SOL_TXT (Additional credit standing information), SOL_I_D (Date of Credit Standing Information) and RATING (Rating) of the Financial Services Business Partner table Creditworthiness Data (table name BP1010 ) will become obsolete in a future release. The data contained in these fields have to be migrated to the ratings table BP1012. This note has the purpose to make you aware of this change. The migration can already be executed by customers now, however only if they do not use either of the applications Loans Management and Treasury Management, which still access the 4 fields that will become obsolete.

The migration will become mandatory from a future S/4HANA on Premise Release onward, the earliest one being 2025. We will inform you by changing the text of this note (creating a new note version) as soon as we have more detailed information.

## Reason and Prerequisites

The four mentioned fields in Financial Services Business Partner table for Creditworthiness Data must not be used any more from a (to be defined) future S/4HANA release onwards. Reason is that these fields have the character of a rating and for ratings there is a separate table available. Another reason is that these fields are not contained in our BAPIs for Creditworthiness Data

(BAPI_BUPA_CREDIT_STANDING_GET/SET), because of this these fields can only be used locally in a system via transaction BP, there is no possibility to replicate the data in these fields to other systems.

A migration report is already available. It can be used to migrate these fields into a rating entry in table BP1012. At the moment this migration must not be executed as long as you use either of the applications Treasury Management, Loans Management, Statutory Reporting, Credit Management. We will update this note as soon as there is any change. Currently you can keep everything as is, you do not need to execute the migration. In case you use one of the abovementioned applications, please refrain from executing the migration. In case you do not use either of the abovementioned applications you may continue and execute the migration. In case of questions please open a case on component FS-BP.

When you try to execute the steps described in the migration note (see solution part bellow) it may happen that you get an error because there is no business function available for the switch FSBP_MIGCS_SWITCH. In this case implement note 3327581 in your system. In order to check if the business function for the switch is available in your system you may use transaction SFW5. Business function name is FSBP_MIGRATION_CS_TO_RATING and can be found under node "Enterprise Business Functions".

## Solution

## Procedure for determining the relevance (relevance condition):

"The migration needs to be executed if there is at least one entry in one of the four mentioned fields of table BP1010 in any of the clients of your system apart from 000 and 066."

We have also provided a consistency check class that is triggered by the SUM process. Currently the SUM process does not return any warning or error if the relevance condition is true. But as soon as we enforce the migration in a future release our check class will return an error and the SUM process will be stopped, in case the above relevance condition is true. With this the migration will then be enforced.

## Required and recommended actions

In case you do not use TRM or CML applicaiton you may already now execute the migration from BP1010 to BP1012 (for the 4 obsolete fields). See below for more details.

Currently - however - it is not possible to activate switch FSBP_MIGCS_SWITCH, which would remove the 4 obsolete fields from transaction BP and corresponding IMG activities from transaction SPRO. Reason is that there is no business function assigned to this switch. We are currently working on the creation of a business function. As soon as the business function is available we will update this note.

If you would like to execute the conversion (provided that you do not use TRM and CML), please find information below how to execute the migration.

In SAP note 1765305 (after new business function is available we will probably provide a new note) you can find an ASU Toolbox Content XML file that can be started using the so-called ASU-Toolbox. With this you are guided through the migration. Activating the business function is currently not possible, the other steps should however be possible, so that you can execute the migration.

The main steps are the following:

Activate business function FSP_FSBP_MIGRATION_CS (manual step) (currently not yet possible!)

Check whether data needs to be converted (automatic step when executing the XML in the ASU toolbox)

Analyze and configure Customizing settings for mapping (Customizing - manual step)

Execute Report FSBP_MIGCS_MAPPING_EDIT for customizing assignment (automatic step)

Mass conversion of credit standing data to ratings (report FSBP_MIGCS_MASS_MIGRATION, automatic step)

You will be guided through the whole process supported by the system after starting ASU toolbox. For details how to start this guided process please check note 1765305 and the referenced note 1000009.

## Other Terms

SAP Business for Financial Services, Business Partner, SAP BP, FSBP, SOL_INS, SOL_TXT, SOL_I_D, RATING, BP1010, BP1012, Creditworthiness data, ratings, Simplification, item, simplification item, migration,
