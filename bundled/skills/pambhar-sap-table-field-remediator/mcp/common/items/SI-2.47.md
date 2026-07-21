---
item_id: SI-2.47
title: "2.47 S4TWL - Ariba Network Integration"
pages: 109-113
sap_notes: [2182725, 2237932, 2246865, 2341836, 2406571, 2502552, 2705047]
components: [BNS-ARI-SE]
objects: []
---
Application Components:BNS-ARI-SE

Related Notes:

| Note Type       |   Note Number | Note Description                                                    |
|-----------------|---------------|---------------------------------------------------------------------|
| Business Impact |       2341836 | S4TWL - Ariba Network Integration in SAP S/4HANA on-premise edition |

## Symptom

You are planning a system conversion from SAP ERP to SAP S/4HANA on premise. The information below is important.

## Solution

This SAP Note is relevant if you use the SAP ERP add-on of Ariba Network Integration 1.0 for SAP Business Suite. In SAP S/4HANA, Ariba Network integration functionality

is not provided as an add-on but as part of the SAP S/4HANA core product. Not all integration processes and messages that are provided with Ariba Network Integration 1.0 for SAP Business Suite are available in SAP S/4HANA. After the conversion from SAP ERP to SAP S/4HANA, the integration of processes and cXML messages listed below are not nativly supported by SAP S/4HANA.

Please take into account that there will be no further development of new features or functionalities for the S/4HANA native Ariba Integration. You should consider a transition to the SAP Ariba Cloud Integration Gateway as soon as possible. More details are provided in the note 2705047 (Roadmap for Ariba Integration Solutions).

The preferred approach to migrate the ERP add-on of Ariba Network Integration to the S/4HANA on-premise edition would be first to convert this add-on to the SAP Ariba Cloud Integration Gateway and only then start the ERP system converion. See Migrating from SAP Business Suite Add-On.

## Business Process Related Information

Note the restrictions for SAP S/4HANA, on-premise edition 1511 listed below.

The following processes are not supported:

Processing of CC invoices (invoices transfered from SAP S/4HANA to Ariba Network)

Service procurement/invoicing process

Payment process

Discount management process

Update of Advanced Shipping Notifications

Ariba Supply Chain Collaboration e.g.

Processing of scheduling agreement releases

Consignment process

Subcontracting process

Processing of forecast data

Multi-tier purchase order processing

Purchase order return items processing

Integration processes for suppliers Quality Management Process (e.g. Quality Notificiaton, Quality Inspection, Quality Certificates...)

The following cXML message types are not available:

ReceiptRequest

CopyRequest.InvoiceDetailRequest

ServiceEntryRequest

PaymentRemittanceRequest

PaymentRemittanceStatusUpdateRequest

PaymentProposalRequest

CopyRequest.PaymentProposalRequest

ProductActivityMessage

ComponentConsumptionRequest

ProductReplenishmentMessage

QuoteRequest

QuoteMessage

QualityNotificationRequest

QualityInspectionRequest

QualityInspectionResultRequest

QualityInspectionDecisionRequest

ApprovalRequest.ConfirmationRequest

OrderStatusRequest

Note the restrictions for SAP S/4HANA, on-premise edition 1610, 1709, 1809 and 1909 listed below.

The following processes are not supported:

Processing of FI - CC invoices (transfered from SAP S/4HANA to Ariba Network)

Update of Advanced Shipping Notifications

Ariba Supply Chain Collaboration e.g.

Processing of scheduling agreement releases

Consignment process

Subcontracting process

Processing of forecast data

Multi-tier purchase order processing

Purchase order return items processing

Integration processes for suppliers

Quality Management Process (e.g. Quality Notificiaton, Quality Inspection, Quality Certificates...)

The following cXML message types are not available:

ProductActivityMessage

ComponentConsumptionRequest

ProductReplenishmentMessage

QualityNotificationRequest

QualityInspectionRequest

QualityInspectionResultRequest

QualityInspectionDecisionRequest

ApprovalRequest.ConfirmationRequest

OrderStatusRequest

## Required and Recommended Action

Conversions to 1511 or 1610:  Implement the master conversion pre-check SAP Note "2182725 - S4TC Delivery of the SAP S/4HANA System Conversion Checks" and follow the instructions in this note.

Conversions 1709 and later: Implement the master conversion pre-check SAP Note "2502552  - S4TC - SAP S/4HANA Conversion & Upgrade new Simplification Item Checks" and follow the instructions in this note.

For Ariba Network Integration, also implement the pre-check SAP Note "2237932 S4TC Ariba BS Add-On Master Check for SAP S/4HANA System Conversion Checks". This note is also listed within the master note.

Regarding customer code relevant changes please read the following SAP Note "2406571 - SAP S/4HANA Simplification: Ariba Network Integration (custom code relevant changes)"

If pre-checks fail, see the following SAP Note: "2246865 - S/4 Transition: Activities after failed PreChecks".

Access SAP Note: "2341836 - S4TWL - Ariba Network Integration in SAP S/4HANA on-premise edition", download the following documents, and follow the steps described.

Before the

conversion:  S4H_CONV_INTEGRATION_ARIBA_NETWORK_PREP

C.PDF

After the conversion:

S4H_CONV_INTEGRATION_ARIBA_NETWORK_POSTC.PDF
