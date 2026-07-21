---
item_id: SI-8.4
title: "8.4 S4TWL - SAP Travel Management in SAP S/4HANA Suite"
pages: 249-255
sap_notes: [2719018, 2892303, 3260453, 3296253]
components: [FI-TV]
objects: []
---
Application Components:FI-TV

Related Notes:

| Note Type       |   Note Number | Note Description                                   |
|-----------------|---------------|----------------------------------------------------|
| Business Impact |       2719018 | S4TWL - SAP Travel Management in SAP S/4HANA Suite |

Symptom This is an information note, which contains the scope of the new product "SAP Travel Management for SAP S/4HANA".

## Reason and Prerequisites

You are doing a system conversion from Business Suite to SAP S/4HANA, on-premise edition.

## Solution

This note contains in attachment the migration guide for customer who want to migrate from Business Suite to S/4HANA Suite.

SAP Travel Management is not available for SAP S/4HANA Cloud, public edition. SAP Travel Management is available for SAP S/4HANA Cloud, private edition as an option for those customers moving from SAP ERP ECC or SAP S/4HANA, that cannot move to SAP Concur right away and is mainly designed for SAP Installed Base customers to protect their investments.

The scope will be comparable to the one in S/4HANA compatibility scope pack corresponding to ECC 6.0 Enhancement package 8.

It is not necessary to change from ERP to the compatibility mode of SAP S/4HANA. Customers can switch directly to the SAP S/4HANA system (release 2022 or upper versions).

The migration process is comparable to a new release installation. There is a migration guide to assist customers with the migration.

Additional information: There will be no major change as the architecture stays the same (database / SAP GUI applications, Web Dynpro applications, Workflows, Transfer to Accounting/Payroll etc.).

The new product will be compliant with S/4HANA standards

Adoption of the GDPR framework for archiving, data deletion, RAL*, etc.

Accessibility

Performance (Fiori apps old/new)

Display harmonization

The major difference is the availability of a set of new FIORI applications based on Fiori Element Framework with CDS views and RAP Technology.

The new Fiori Applications are based on the same customizing than the previous Fiori versions (V1 & V2 and WebDynpro), there is no new customizing to configure. The approval applications (My-Inbox) will be based on a new Odata Service for the display of the information, but there is no major change and you can reuse your own configuration in the same way. In S/4HANA for accessibility reason only the PDF forms are allowed, you will not be able to use HTML Form in standard.

Two new roles are available in this context the "Business Traveler" role and the "Traveler Assistant" role. Corresponding to the roles, two new "Business Catalogs" are available in standard.

Here the list of new Fiori applications:

For "Business Traveler" role

My Travel Requests for Business Traveler (Fiori ID F6015)

My Travel Plans  for Business Traveler (Fiori ID F6768)

My Travel and Expenses  for Business Traveler (Fiori ID F6190)

My Credit Card Transactions (Fiori ID F6506)

For "Traveler Assistant" role

Travel Requests for Travel Assistant (Fiori ID F0409B)

Travel Plans for Travel Assistant (Fiori ID F6771)

Travel and Expenses for Travel Assistant (Fiori ID F0584B)

For the Public Sector Germany, two new processes : Relocation and separation allowance will be available for customers. Both processes will be available for Domestic or International trips.

German Regulation of International Separation Allowances (ATGV)

German Law on Inland Relocation Costs (BUKG)

German Regulation of Foreign Relocation Costs (AUV)

The initial shippement will not include all existing features. The existing gaps will be filled in the next FSPs. For an exhaustive list of limitations please check the following information underneath:

Country versions for CEE (Central and Eastern Europe).

Public Sector-specific features like Relocation and Separation allowance are available in SAP GUI transaction only and are not part of the new Fiori applications.

Table PTK99: The use of table PTK99 is not supported. Instead we provide an extensibility concept (please see SAP KBA 3296253 and 3260453). If you want to manage old data in the cluster corresponding to the structure PTK99, you will need to manage the mapping between the old structure (PTK99) and new structures yourself via extensibility concept.

Merge of receipts are not supported: Not for initial shipment, planned for futur releases

Concurrent assignment: Not for initial shipment planned for futur releases (HCM dependency), this feature is provided centrally by HCM.

## List of Transactions Deprecated in S/4HANA:

All transactions around travel planning or in relation with old technology are not relevant anymore and will be marked as "Deprecated" in a first step and "Obsolete" later.

Here the definition of Deprecated and Obsolete statuses:

(computing) (of a software feature) to be considered outdated and best avoided and planned to be removed in near future release even though you can still use it now , usually because it has been replaced with a newer feature.

Deprecated

Obsolete Therefore, it means the UI / functionality still works and is officially supported but is not recommended to be used anymore. No improvements / new features can be expected. In the foreseeable future it is planned to make it obsolete (see below) in favor of the designated successor UI / functionality.

(computing) no longer valid, no longer works as expected, must not be used .

Therefore, it means The UI / functionality must not be used anymore. It is either significantly restricted in functionality (e.g. view only mode) or no longer supported at all. Customers cannot expect that it works correctly. It is recommended that execution is blocked. The UI could be finally removed from the system at a later point in time. The designated successor UI / functionality must be used instead at this phase.

Here the list of transactions marked deprecated for the release S/4HANA 2022

| Transaction   | Name                           | Successor   |
|---------------|--------------------------------|-------------|
| PR01          | Maintain (Old) Trip Data       | PR05        |
| PR05_ESS      | Travel Expense Manager via ESS |             |

PR20

Create Trip

PR05

PRAA

Automatic Vendor

Maintenance

BP

PRCC_CDF3

Obsolete; Use

PRCC_CDF3_V2

PRCC_CDF3_V2

PRCT

Current Settings

SPRO

PREX

Create expense report

TRIP

PRPL

Create Travel Plan

TRIP

PRRQ

Create Travel Request

TRIP

PRTAXFIN

Tax Report Finland

PRCRKATRE

PRTC

Display Imported Documents

PRCCD

PRTS

Overview of Trips

PRTE

PRWW

Expense Reports (Offline)

PTRV_OFFLINE

Activate Offline Travel

Manager

PTRV_RTREE

Display Trav. Management

Report Tree

SE43

TRIP_EWT

Travel Manager

PR05_ESS

ITS Service

PRWW

ITS Service

TP10

Travel Plan Synchronization

(AIR)

TP12

Travel Plan Synchronization

(Manual)

TP14

Travel Plan Synchronization

(Queue)

TPLOG

Short cut for TPLOG TP_LOG

VPNR

View of the active PNR in 1A

AMADEUS

Amadeus Direct

APOLLO

Apollo Bypass

BYPASS

Bypass for All Reservation

Systems

FITP_RESPO

Contact Partner

Responsibilities

FITP_SETTINGS

Settings for Travel Planning

FITP_SETTINGS_TREE

Tree Maintenance Current

Settings

GALILEO

Galileo Bypass

GALILEO_SYNCH

Synchronization of Galileo

PNRs

GALILEO_VPNR

Galileo Bypass VPNR

HUGO

Settings for Travel Planning

TP01

Planning Manager

TP02

Travel Planning (End User)

TP02_EWT

Travel Planning (End User)

TP03

Planning Manager (Expert)

TP04_EWT

Travel Request (End User)

TP20

Create Travel Plan

TP30

Display Travel Planning report

tree

TP40

Maintain Routings

TP41

Initial Screen via IMG

TP50

Global flight availability

TP60

Synchronization of Hotel

Catalog

TPPF_D

Display Entry V_TA23PF by

Key

TPPR

Travel Profile Display

TPQ0

Quicktrip Manager

SABRE

SABRE Bypass

SABRE_PNR

Display a Sabre PNR

SABRE_VPNR

SABRE Bypass VPNR

TPLP

Create/Change LPs for

SABRE

PR_WEB_1000

Trip Data

PR_WEB_1200

General Trip Data

PR_WEB_1300

Trip Receipts

PR_WEB_1400

Trip Deductions

PR_WEB_1500

Trip Advances

PR_WEB_1600

Trip Destinations

PR_WEB_1700

Cost Distribution: Trip

PR_WEB_1710

Cost Distribution for Receipts

PR_WEB_1720

Cost Apportionment

Destinations

PR_WEB_1730

Cost Distribution:

Miles/Kilometers

PR_WEB_1800

Legs of Trip

PR_WEB_1900

Check Trip

## Fiori Application

Successor

F0409 Travel Request V1

Obsolete

F0409B My Travel Requests (S/4

HANA)

F0409A Travel Request V2

Deprecated

F0409B My Travel Requests (S/4

HANA)

F0584 Travel &Exp V1

Obsolete

F0584B My Travel & Expenses (S/4

HANA)

F0584A Travel & Exp V2

Deprecated

F0584B My Travel & Expenses (S/4

HANA)

In addtion, the usage of XI interface is not supported in S/4HANA, the booking of Train ticket with BIBE ot Hotel Reservation with HRS is not allowed with XI interface.

These services are available only with our partners (Amadeus and Sabre with the respectives products cytric and GetThere).

For more information please check the note  2892303 - Travel Planning External content

## Other Terms

SAP Travel Management, S/4HANA, S4HCM
