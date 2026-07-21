---
item_id: SI-2.32
title: "2.32 S4TWL - Business User Management"
pages: 77-87
sap_notes: [2340095, 2548303, 2567604, 2570961, 2571544, 2591138, 2763781, 2883989]
components: [BC-SEC-USR-ADM, CA-HR-S4]
objects: []
---
Application Components:BC-SEC-USR-ADM, CA-HR-S4

Related Notes:

| Note Type       |   Note Number | Note Description                                     |
|-----------------|---------------|------------------------------------------------------|
| Business Impact |       2570961 | Simplification item S4TWL - Business User Management |

## Symptom

You need information about Business User Management in SAP S/4HANA.

## Reason and Prerequisites

Business User Management in SAP S/4HANA is mandatory and is automatically activated during the conversion from SAP Business Suite to SAP S/4HANA.

## Solution

What Has Changed in Business User Management in SAP S/4HANA?

What is the difference between business users and SU01 users?

What is the business impact of that change?

Limitations User Management Business Partner Human Capital Management (HCM)

HCM Integration active or inactive: What does it mean?

HCM Integration Switch (System Table T77S0)

External Resources Switch (System Table T77S0)

How to create Business Users in SAP S/4HANA

HCM Integration is Active

HCM Integration is Inactive

Maintenance of the Business User Workplace Address

Conversion

How to Determine Relevance

## What Has Changed in Business User Management in SAP S/4HANA?

SAP S/4HANA is introducing a new identity model for business users, which is based on the "principle of one". A business user is defined as a natural person who is represented by a business partner and a link to a user in the system. Business users interact with the software in the context of a business process, for example, in the role of a purchaser, a sales representative, or a production planner.

In SAP S/4HANA, the business partner is the natural person who maintains the user data for the person, work center, and communication-related information. For logon, changing the user ID (BNAME) is no longer supported. However, one person can still log on with a user alias or email. The user alias or email can be changed (see SAP Note 2883989). The identity model for business users ensures correct auditing, workflows, and jobs. It also avoids errors in documents after a change of the user ID (BNAME). Auditors require a consistent history of all documents that contains the user ID (BNAME).

SAP S/4HANA Business User Management enables and supports the entire life cycle maintenance of business users such as organizational changes, change of employment, or retirement. A user in SAP S/4HANA has a one-to-one relationship with a corresponding business partner (natural person). This reduces redundant maintenance and prevents outdated information.

## What is the difference between business users and SU01 users?

The business user is a SU01 user, but also has a one-to-one relation to the corresponding business partner. This relationship is time independent and cannot be changed anymore. For more details about important user related constraints see SAP Note 2571544.

The business user concept is used in many new applications in SAP S/4HANA. SU01 users with Classic Address (Identity Address Type 00 - User's Old Type 3 Address) lead to limitations because the new business user model is a prerequisite for many business applications. As soon as Fiori apps are activated and used, business users are mandatory (for example Teams, CreditAnalyst in Credit Management or Situations).

The business partner contains the personal information, for example private address, workplace address, bank details, vendor and customer related data. The business partner and SU01 user share personal details and workplace address related data. The advantage of the new business user model is that the entire lifecycle of that person works without redundant maintenance of user address data. Business users can still be managed using transaction SU01, Central User Administration or identity management systems.

In the SAP Business Suite, you can use transaction BP (Business Partner Maintenance) to assign users to business partners. In SAP S/4HANA this is not possible anymore to avoid an inconsistent data model for business users. Existing business partners cannot be converted to business users, because of Data Protection and Privacy (DPP). Already existing business partners could have been part of a distribution scenario.

## What is the business impact of that change?

With the new business user model in SAP S/4HANA we have a clear maintenance ownership. It can be owned by Human Capital Management (HCM), Business Partner (BP) or User Management. The ownership of HCM is only relevant when HCM integration is active. (More details about HCM integration see section HCM Integration active or inactive: What does it mean?)

Using the example of SU01 the following data categories exist:

Person: The personal data for the business user is derived from the corresponding business partner. In case HCM integration is active this data is mapped from the corresponding employee of the HCM system (SAP SuccessFactors or SAP HCM).

Work Center: The work center data for the business user is derived from the workplace address of the corresponding business partner. In case HCM integration is active, the function and department fields are mapped by default from the corresponding employee of the HCM system (for customizing options, see SAP Note 2548303).

Communication: The communication data for the business user is derived from the workplace address of the corresponding business partner (for customizing options, see SAP Note 2548303).

Company: During the conversion of a SU01 user from SAP Business Suite (classic user) to a business user in SAP S/4HANA the company address is copied to the business partner workplace address.

## Limitations - User Management

Due to the new business user model the database view USER_ADDR can no longer be used in SAP S/4HANA. This view can only display the users with classic address but not the business users. It is not possible to enhance this view. Instead of the database view USER_ADDR use the search help USER_ADDR (which is equivalent to an official API for searching users). In exceptional cases, you can use the SAP internal CDS view P_USER_ADDR, but have in mind that it can be changed by SAP at any time. With the ABAP statement "with privileged access" the authorization check is ignored. As a reference, use the coding of the search help exit F4IF_USER_ADDR_SUID_EXIT.

## Limitations - Business Partner

In general, business partners that are neither employee nor contingent workforce cannot be managed as business users.

In transaction BP (Business Partner Maintenance) you can no longer assign SU01 users to business partners in SAP S/4HANA. This feature has been removed.

You can no longer maintain the following fields in transaction BP (Business Partner Maintenance):

Personnel Number (BUS000EMPL-EMPLOYEE_ID)

User (BUS000EMPL-USERNAME), for example, shown for role category WFM001 (Resource)

Internet User (BUS000EMPL-INTERNETUSER), for example, shown for role category BUP005 (Internet User)

You can no longer assign the roles belonging to the following role categories in transaction BP:

Employee (BUP003)

Freelancer (BBP010) → Contingent worker

External Resource / Service Performer (BBP005) →  Contingent worker with additional supplier relation (staffed from external supplier)

Collaboration Business User (BUP012)

Resource (WFM001) → Only needed for SAP Portfolio and Project Management (component PPM-PFM-RES).

This means you have to create the business partners in one of the mentioned role categories. (New Procedures see section How to create Business Users in SAP S/4HANA)

Existing business partners cannot be expanded by the following role categories later on: Employee, Freelancer, Service Performer. The reason is business partners with the referenced roles have special behavior regarding:

Authorization management (driven by GDPR/DPP requirements)

Replication/distribution (no replication from SAP S/4HANA to any system)

For business partners which are assigned to one of these role categories, the fields of the following field groups cannot be maintained via transaction BP or the customer/supplier master Fiori UIs (independent from whether HCM integration is active or inactive):

Field group 1: Partner Number (+ Role for Change Doc. Display)

Field group 8: Form of Address

Field group 9: Bank Details (for bank detail's ID HC*)

Field group 25: Person: First Name

Field group 26: Person: Academic Title

Field group 29: Person: Correspondence Language

Field group 30: Person: Complete Name Line

Field group 33: Person: Gender

Field group 38: Person: Birth Name

Field group 41: Person: Middle Name

Field group 43: Person: Initials of Person

Field group 54: Person: Last Name

Field group 61: Address: Address Usage (HCM001, HCM002). Note that the address data can be edited in transaction BP but will be overwritten by the periodically scheduled sync report /SHCM/RH_SYNC_BUPA_FROM_EMPL.

Workplace address (table MOM052) attributes such as phone number or email address are not displayed in transaction BP. There are no plans to enhance transaction BP as of now. Please use transaction SU01 to display the workplace address attributes.

Relationships of relationship category BUR025 (Service Provider) cannot be maintained for roles of role category BBP005 (Service Performer).

Business partners which are assigned to one of these role categories cannot be maintained using SAP Master Data Governance for business partners, customers or suppliers.

The usage of such workforce business partners in SAP Master Data Governance is also restricted:

In partner function maintenance: Only the ID of the workforce business partners is visible, and navigation to that business partner is not possible.

In business partner relationships: Relationships to workforce business partners are not visible and thus can't be maintained.

Limitations - Human Capital Management (HCM)

In case of multiple employments (concurrent / global employment / country transfer) only the main employment is allowed to have a user assigned. Additional user assignments are not allowed.

## HCM Integration active or inactive: What does it mean?

HCM integration active means that you rely on the HR mini master (HR infotype based PERNR data model including the PA-Tables). This HR mini master can be locally maintained (for example via transaction PA30 or PA40) or via real integration scenarios with SAP SuccessFactors Employee Central or an external (third party) HCM system.

If you don't need the HR mini master you should deactivate HCM integration.

Based on the HCM integration, business users are handled the following way:

If the HCM integration is active, it is mandatory to schedule the sync report /SHCM/RH_SYNC_BUPA_FROM_EMPL regularly as a background job so that the business users are automatically synchronized with the PA-Tables. You can maintain business users via

Transaction PA30 or PA40

HCM integration.

If the HCM integration is inactive, you can maintain business users via

Fiori app Maintain Employees

Fiori app Maintain External Resources

SOAP Service ManageBusinessUserIn

Report RFS4BPU_IMPORT_BUSINESS_USER.

An example of why we need the HCM integration:

For using the standard SD partner functions for employees, it is necessary to maintain the employees with the features of the HCM compatibility pack in SAP S/4HANA. It is not sufficient to maintain persons without active HCM integration (see SAP Note 2763781).

| HCM Integration Switch (System Table T77S0)   | HCM Integration Switch (System Table T77S0)   | HCM Integration Switch (System Table T77S0)   | HCM Integration Switch (System Table T77S0)   | HCM Integration Switch (System Table T77S0)   |
|-----------------------------------------------|-----------------------------------------------|-----------------------------------------------|-----------------------------------------------|-----------------------------------------------|
| Description                                   | Group (GRPID)                                 | Sem. abbr. (SEMID)                            | HCM Integration inactive                      | HCM Integration active                        |
| Activate HCM Integration                      | HRALX                                         | HRAC                                          | SPACE (Blank)                                 | X                                             |
| Integration P-BP Activated                    | HRALX                                         | PBPON                                         | OFF                                           | ON                                            |

HCM Integration for External Resources (BBP005) is set by the External Resources Switch. It interacts with the HCM Integration Switch as follows:

| External Resources Switch (System Table T77S0)   | External Resources Switch (System Table T77S0)   | External Resources Switch (System Table T77S0)   | External Resources Switch (System Table T77S0)   | External Resources Switch (System Table T77S0)   | External Resources Switch (System Table T77S0)   | External Resources Switch (System Table T77S0)   |
|--------------------------------------------------|--------------------------------------------------|--------------------------------------------------|--------------------------------------------------|--------------------------------------------------|--------------------------------------------------|--------------------------------------------------|
| Description                                      | Group (GRPID)                                    | Sem. abbr. (SEMID)                               | HCM Integration inactive                         | HCM Integration inactive                         | HCM Integration inactive                         | HCM Integration active                           |
| Activate External Resources Switch               | HRALX                                            | PEXON                                            | OFF                                              | OFF                                              | ON                                               | ON                                               |
| Activate HCM Integration                         | HRALX                                            | HRAC                                             | SPACE (Blank)                                    | X                                                | SPACE (Blank)                                    | X                                                |
| Integration P-BP Activated                       | HRALX                                            | PBPON                                            | OFF                                              | ON                                               | OFF                                              | ON                                               |

## How to create Business Users in SAP S/4HANA - HCM Integration is Active

The HR mini master is the origin of business users (see HCM simplification SAP Note 2340095). The user assignment in the HR mini master has to be maintained in infotype 105 subtype 0001.

The creation of business users is managed by the periodically scheduled sync report /SHCM/RH_SYNC_BUPA_FROM_EMPL. This report performs the following steps:

Creation of business partner in one role of the role categories Employee (BUP003), Freelancer (BBP010) or External Resource / Service Performer (BBP005) with

private address bank details workplace address customer/vendor related data (see Customer Vendor Integration [CVI])

relationships

Assignment of SU01 user. If the user doesn't exist, then the assignment takes place once the SU01 user is created.

Errors of the sync report are stored in the application log. The application log can be accessed via transaction SLG1 (or SLGD) for object SHCM_EE_INTEGRATION, Subobject BUPA_SYNC (filter via External ID field to Personnel Number PERNR).

## Exception:

The creation of Collaboration Business User (BUP012) and Resource (WFM001) does not work with sync report /SHCM/RH_SYNC_BUPA_FROM_EMPL. They can only be created by using the following Fiori apps:

| Fiori ID   | App Title                    | Business Partner Role Category   | As Of Release   | Comments                                                                      |
|------------|------------------------------|----------------------------------|-----------------|-------------------------------------------------------------------------------|
| F4911      | Maintain Collaboration Users | BUP012                           | 2020 FPS01      |                                                                               |
| F3505      | Maintain Resources           | WFM001                           | 1809 FPS01      | Only needed for SAP Portfolio and Project Management (component PPM-PFM-RES). |

## How to create Business Users in SAP S/4HANA - HCM Integration is Inactive

There are three options to create business users:

Business users can be created in SAP S/4HANA by using the following Fiori apps (including CSV import for mass processing):

| Fiori ID   | App Title          | Business Partner Role Category   | As Of Release   | Comments   |
|------------|--------------------|----------------------------------|-----------------|------------|
| F2288A     | Maintain Employees | BUP003                           | 2020 FPS01      |            |

| F2288   | Maintain Employees           | BUP003   | 1709 FPS02   | Replaced by Fiori app F2288A.                                                 |
|---------|------------------------------|----------|--------------|-------------------------------------------------------------------------------|
| F4911   | Maintain Collaboration Users | BUP012   | 2020 FPS01   |                                                                               |
| F3505A  | Maintain External Resources  | BBP005   | 2020 FPS01   |                                                                               |
| F3505   | Maintain Resources           | WFM001   | 1809 FPS01   | Only needed for SAP Portfolio and Project Management (component PPM-PFM-RES). |

For mass maintenance, you can also use the report

RFS4BPU_IMPORT_BUSINESS_USER (As of SAP S/4HANA 1809). For SAP S/4HANA 1610 you can use report RFS4BPU_EMPLOYEE_UPLOAD - see SAP Note 2567604.

SOAP Service ManageBusinessUserIn - can be set up via SOA Manager (Transaction SOAMANAGER).

## Maintenance of the Business User Workplace Address

There are three possible application areas to maintain the workplace address of the business user:

Human Resources (HR)

Business Partner Management (BP)

User Management (US)

SAP S/4HANA 1709 FPS02 provides a configuration view that defines the maintenance source of the workplace address attributes. SAP delivers a default proposal for both variants, HCM integration active/inactive. See SAP Note 2548303 for details. This configuration ensures that updates to the workplace address are restricted to one dedicated application area.

The configuration view TBZ_V_EEWA_SRC can be set via Transaction SPRO (SAP Reference IMG) Under 'SAP Business Partner' at node 'Additional customizing for SAP Business Partner' (see SAP Note 2591138).

The configuration view has the following constraints:

If a field is configured for the application area User Management and the Central User Administration (CUA) is active, the maintenance rules of the CUA apply. (Transaction SCUM)

If the HCM integration switch is active, BP is not applicable as maintenance source.

If the HCM integration switch is inactive, HR is not applicable as maintenance source.

The location part of the workplace address (company address - transaction SUCOMP) is not part of configuration view TBZ_V_EEWA_SRC because it can only be maintained by User Management. (See SAP Note 2571544)

## Conversion

If HCM integration is active and the conversion from SAP Business Suite to SAP S/4HANA is done, employees are automatically converted to business users via the periodically scheduled sync report /SHCM/RH_SYNC_BUPA_FROM_EMPL.

## If HCM integration is inactive:

Business partners that exist in an ERP system with user linkage via table HRP1001 from BP-CP-US are automatically converted to business users in SUM-Phase as of SAP S/4HANA 1809 (see conversion report RFS4BPU_CONVERT_BUSINESS_USER).

Business partners that exist in an ERP system with user linkage via table BP001 are automatically converted to business users in Silent Data Migration (SDM) as of SAP S/4HANA 2020 (see class CL_SDM_BUPA_BPU_BP001).

## How to Determine Relevance

Simplification item S4TWL - Business User Management is relevant for all SAP S/4HANA conversion customers.
