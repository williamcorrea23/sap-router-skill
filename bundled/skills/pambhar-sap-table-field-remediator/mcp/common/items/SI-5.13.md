---
item_id: SI-5.13
title: "5.13 S4TWL - Risk Determination and Pricing for MM Contracts not supported yet"
pages: 202-203
sap_notes: [2560298]
components: [LO-CMM-BF, LO-CMM-ANL]
objects: []
---
Application Components:LO-CMM-BF, LO-CMM-ANL

Related Notes:

| Note Type       |   Note Number | Note Description                                                            |
|-----------------|---------------|-----------------------------------------------------------------------------|
| Business Impact |       2560298 | S4TWL - Commodity Pricing in Purchasing Contracts and Scheduling Agreements |

## Symptom

Within S/4HANA 1709 - from FPS00 until FPS02, MM Contracts and Scheduling Agreements do not support the following functionality:

Risk Distribution Plan (RDP)

Usage of Commodity Pricing Engine (CPE) and Configurable Parameters and Formulas (CPF)

Starting with S/4HANA 1709 FPS03, MM Contracts are supported with the following functionality:

Usage of Commodity Pricing Engine (CPE) and Configuable Parameters and Formulas (CPF) using time independent conditions (document conditions). Existing MM Contracts (with time-dependent conditions) have to be closed and new MM contracts with time independent conditions have to be created for the open quantity and validity period.

Risk Distribution Plan (RDP) for time independent conditions.

Starting with S/4HANA 2020 FPS00 Scheduling Agreements are supported with commodity pricing (CPE, CPF) using time-dependent conditions.

## Solution

Before S/4HANA 1709 FPS03, Customers converting to S/4HANA using RDPs or CPE/CPF within MM Contracts or Scheduling Agreements cannot convert.

## Other Terms

RDP, CPE, CPF, Purchasing Contract, Scheduling Agreements
