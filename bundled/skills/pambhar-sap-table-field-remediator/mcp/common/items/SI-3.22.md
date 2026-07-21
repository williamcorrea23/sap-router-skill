---
item_id: SI-3.22
title: "3.22 S4TWL - Material Number Field Length Extension"
pages: 162-171
sap_notes: [1597790, 1696821, 2214213, 2215424, 2215852, 2216958, 2229860, 2229892, 2232362, 2232366, 2232391, 2232396, 2232497, 2233100, 2267140, 2270396, 2270836, 2333141]
components: [LO-MD-MM, CA-FLE-MAT]
objects: [MATNR]
---
Application Components:LO-MD-MM, CA-FLE-MAT

Related Notes:

| Note Type       |   Note Number | Note Description                               |
|-----------------|---------------|------------------------------------------------|
| Business Impact |       2267140 | S4TWL - Material Number Field Length Extension |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Reason and Prerequisites

In SAP S/4HANA, the material number field length has been extended from 18 to 40 characters. This change was first implemented in SAP S/4HANA, on-premise edition 1511 and affects this release and higher releases.

## Solution

SAP S/4HANA can support a material number with 40 characters. The appropriate related SAP development entities (domains, data elements, structures, table types, and transparent tables, external and internal interfaces, user interfaces, and so on) have been adapted accordingly. Where required, automated logic is in place and executed automatically in case a customer converts his current SAP Business Suite system into SAP S/4HANA.

Nevertheless there might be constellations where a customer needs to be aware about. For example:

In certain constellations there might be the requirement to adapt custom code related to the material number field length extension.

In a multi-system landscape, the customer has to decide if and when to switch on the extended material number functionality, as the switch impacts how compatible the system communicates within a system landscape.

In the following chapters, the different aspects of the material number field length extension are described.

This note focuses on the neccessary technical adjustments which are a consequence of the field length extension. These adjustments are relevant regardless of the intention to enable the extended length for material numbers in customizing or not. The decision for activation of the extended length needs to be taken based on business requirements and considering the restrictions outlined in this note, the notes referenced in this note and is completely independent of the required technical adjustments.

## Overview

With SAP S/4HANA, on-premise edition 1511, the maximum field length of the material number was extended from 18 to 40 characters.

The material number field length extension was done with SAP S/4HANA and is available starting with the SAP S/4HANA, on-premise edition 1511. For the first step into SAP S/4HANA - SAP Simple Finance, on-premise edition 1503 - the maximum field length is still 18 characters long. Additional remark: SAP S/4HANA Finance 1605  based on Enhancement Package 8 is as well be based on an 18 characters long material number.

## Consistent Usage in System-Internal Coding

Extending the material number means that in the coding within the system it must be ensured that 40 characters can be handled at all relevant coding places. Especially, it must be made sure that the material number will not be truncated to its former length of 18 characters as this would result in data loss.

In an SAP system, this consistent behaviour is usually ensured by the fact that all data elements used to type relevant fields are derived from the same domain, the domain defining the technical length of the derived fields. Whenever coding uses these fields, the coding is automatically adapted when the domain changes.

For the material number itself we identified the domains that are used to define material number fields. All these domains have been extended to 40 characters.

Besides these direct usages of the material, it may be that a specific material is also used in other fields. An example may be characteristic values: A material may well be used as characteristic value. For all such fields for which a material - besides other possible values - is a valid content, it has been checked that these fields are long enough to hold the extended material number. These fields (or the underlying domains) have been extended as well. Extending further - dependent - fields of course means that the usages of the fields have been investigated as well.

Extending such 'target' fields  which are not material numbers by themselves was only done if the material number needs to be handled in the field, as extending a field usually trigger follow up changes. At several places, the material number is used as reference, template, or for other reasons but another (shorter) value, for example, a GUID, could be used as well. In these and other similar cases, it may be the better choice to switch to another value. Using this other value has been done at all places where this was appropriate.

Overall, the complete data flow in the system has been analysed to identify all places at which a material number was moved to a field that was not long enough for a 40 character material number. All these conflicts have been handled in one of the ways described above. Such an analysis also needs to be done in customer or partner coding.

The described changes have also been applied to parameters of all interfaces that are usually called only within one system, that is, local function modules, class methods, BAdIs etc. In the types and structures used as parameters in these local calls, the material number has simply been extended to 40 characters. The same is true for other extended fields as well. This was usually also done for unreleased remote enabled function modules as the main use case for such function modules is an internal decoupling within one system.

For interfaces that are usually called remotely, a different way has been chosen. For more information, see the specific chapter below.

## Storage of the Material Number on the Database

Extending the material number on the database means that the field length of the MATNR field on the database has been extended from 18 to 40 characters. This has been done in all tables (and all fields within the tables) in which a material number can be stored.

Although the maximum length of the database field used to store the material number is now 40 characters, the way how the material number content is stored in the database field has not been changed compared to SAP Business Suite. This means that for such fields usually no data conversion is needed when converting from SAP Business Suite to SAP S/4HANA.

This holds especially true for pure numeric material numbers. With standard Customizing (lexicographic flag not set, i.e. leading zeroes are not significant), pure numeric material numbers are still restricted to 18 characters and will be filled up on the database only up to 18 characters by leading zeroes. This is the same behaviour as in SAP Business Suite.

Overall, the chosen way of storing material number content avoids data conversions in the database. Regarding the storage format for material number content there is no difference between conversion of existing systems and new installations of S/4HANA, the impact on data conversion was merely a factor for the chosen format. Note that data conversion will be needed when a material number is stored in a field that has a concatenated content, and the material number is part of that concatenated content: Concatenation in the code uses the complete technical length of the field (which now is 40 characters) and is also reflected in the database content. This will be explained in detail later in this Simplification Item.

If you have activated the DIMP (Discrete Industries & Mill Products) long material number or manufacturer parts number, the content that is stored in the database for the material number will need to be changed. For further information see the section below and the references therein.

The Material Number in Released External Interfaces Usually a customer has a multi-system landscape: The ERP system is connected to miscellaneous internal and external (SAP or non-SAP) systems. Accordingly, a SAP S/4HANA system with a material number field length of 40 characters needs to consider this multi-system landscape requirement where not all related systems are able to deal with a 40 character material number.

Furthermore, it cannot be assumed that all ERP systems in a customer landscape will be converted to SAP S/4HANA at the same point in time. That means that the external interfaces used for integration have to be compatible to old versions of the interface.

This is especially relevant for the commonly used integration techniques BAPI, RFC, and IDoc as these techniques rely on a fixed length and sequence of fields in the transmitted data. Simply extending the material number field (or other extended fields) in these interfaces would therefore technically break the version compatibility.

We have decided to provide a technical-version compatibility for released external interfaces in the way that is commonly used and proposed for BAPI interfaces: The already existing field keeps its original length and a new field has been added at the end of the structure (or as new parameter) that allows transmitting material numbers with 40 characters.

Besides this, it must be ensured that no material number (or other extended field) can be maintained in the system with a content length greater than the old length of the field. To enforce this and to make the field length extension as far as possible non-disruptive for the SAP S/4HANA customers, the extended material number functionality must be switched on explicitly. Only after this decision it is possible to allow more than 18 characters for the material number.

The changes described have been done for BAPIs, IDocs, and released remote-enabled function modules. This has additionally been implemented where necessary for remote function calls issued by the SAP S/4HANA system and for unreleased remote-enabled function modules that are used to communicate with other SAP Business Suite products like SAP SCM or SAP CRM.

A complete list of relevant function modules, IDocs, and structures that have been extended in this way can be found in the piece lists in the simplification database.

For released WebServices, adding a new field or extending the material number field was not necessary as these services usually already allow material numbers with up to 60 characters in their interfaces.

After an SAP Business Suite System has been converted to SAP S/4HANA or a SAP S/4HANA was newly installed, the extended material number functionality will by default be switched off.

## System Behaviour Depending on the Extended Material Number Switch

If the extended material number functionality is NOT switched on, the system behaves as follows:

After an SAP Business Suite System was converted to SAP S/4HANA, on-premise edition 1511, the B2B and A2A communication via BAPIs, IDOCs, WebServices, released RFCs (inbound), and remotely called RFCs (outbound) still work without further changes.

The shorter versions of the extended fields

are still part of the interfaces.

are still filled when sending data.

are still understood when retrieving data.

If the extended field is used as part of a communicated concatenated field, this concatenated field is still sent in the original field in the old short format and is interpreted in the inbound case in the old short format.

The system prevents that data is created that cannot be sent via the old interface, that is the usage of the extended fields is restricted to the old length.

Communication partners can still rely on the old known behaviour of the interfaces.

The long version of the extended field in the interfaces is filled and interpreted, too. This means that the communication partners can already adapt their interfaces for using the long field although only short material numbers are allowed.

For example, the 18 character material number is also communicated via the 40 character field. This is also true if the extended field is used as part of a communicated concatenated field: the new extended field will contain and expect the new long format.

When extended material number functionality is switched on, the system no longer guarantees that all fields are filled in a way that they can be transmitted via the old fields. Therefore the following applies:

Material numbers and other extended fields can be used with the full length (40 characters).

## That means:

It cannot longer be guaranteed that the old short fields can be filled or accepted: if the material number or other extended fields are used with more than the original length, the shorter version of an extended field cannot longer be filled in the interface and is therefore left empty.

This is also true for concatenated keys containing extended fields. If the value that is part of the concatenate is longer than the original field length, the concatenate can only be sent and evaluated in the new format.

Before SAP S/4HANA, on-premise edition 1511 FPS2 the old short fields have not been filled or accepted when the extended material number functionality is switched on. This has been changed with SAP S/4HANA, on-premise edition 1511 FPS2:

If the current value of the material number or the current value of another extended field still fits into the old short field in the interface, the short field is filled in outbound and accepted in inbound as well.

This is also true for concatenated values: if the old format can still be used because the current value of the extended field contained in the concatenate is short enough, the old format is still sent in outbound and accepted in inbound in the old short field.

Communication partner have to adjust to the new fields and data formats. Be aware: All SAP Business Suite systems are communication partners!

## Internal Calls of External Interfaces

As described in the previous chapters, different strategies have been chosen for internal and for released external APIs.

If a released external API is called internally, that is locally within one system, it is always ensured that the call can be done with new extended field length, no compatibility is required. Therefore - and to be safe when extended material number functionality is activated - all internal calls of external interfaces must only use the newly added extended fields.

This is also true if structures are used internally that are also used in released external interfaces and that therefore have been changed in the way described. Then only the new extended field shall be used in all internal coding, too.

System Settings to Activate the Extended Material Number Functionality

## Note:

If the extended material number functionality is activated in a system, it cannot be easily deactivated as values may exist in different fields that are only allowed with extended material number.

## The Long Material Number within the DIMP Add-On (Discrete Industries & Mill Products)

The extension of the material number is a well-known requirement in SAP Business Suite requested by several customers. An Add-On solution was provided several years ago as part of the industry solution Discrete Industries & Mill Products (DIMP). The so-called DIMP LAMA-functionality is a part of the industry solution Automotive which is one component of the Add-On DIMP (Discrete Industries & Mill Products). See SAP Note 1597790.

Although the industry solution DIMP is part of SAP S/4HANA, the already existing DIMP LAMA-functionality for a long material number (LAMA) will not be part of SAP S/4HANA . In S/4HANA the material number is natively extended to 40 characters. Special conversion steps are needed to migrate the existing DIMP LAMA solution to the new S/4HANA extended material number.

For further information on the conversion of the DIMP LAMA-functionality and the DIMP Manufacturer Parts Number to S/4HANA please check notes 2270396 and 2270836.

ALE Change Pointers

The default setting, both after the move to SAP S/4HANA and for new installations, is that the extended material number functionality is NOT activated. To use a material number with 40 characters, the customer needs to activate this functionality. The following settings are required for that:

Activation of the Extended Material Number Functionality

The activation is realized as client-dependent customizing table.

IMG à Cross-Application Components à General Application Functions à Field length Extension à Activate extended fields

Alternative: Transaction FLETS (For the table maintenance the authorization group FLE [authorization object S_TABU_DIS] is required).

## Changing the Material Number Format

Transaction OMSL allows a customer-specific settings regarding the material number field length. Here the settings need to be adapted to allow a field length of more than 18 characters.

Define Output Format of Material Number can be accessed via IMG (à Logistics General à Material Master à Basic Settings)

ALE change pointer entries related to Master Data Distribution (see SAP Help: LINK) have to be processed completely upfront to the move to SAP S/4HANA. Changes recorded before conversion will no longer be available compatibly after conversion to SAP S/4HANA.

## SAP Notes and Restrictions related to Material Number Field Length Extension

## Conversion Pre-Checks related to Material Number Field Length Extension

It´s recommended to execute conversion pre-check (for details see SAP Note: 2216958). For the conversion of selection variants see SAP Note 1696821 for details.

Note that code adaptions will be needed even if you decide not to activate the extended material number functionality and stay with 18 characters

## Custom Code related information

See SAP Note: 2215424, 2215852

## Restrictions

SAP S/4HANA restriction note:

2214213 for SAP S/4HANA, on-premise edition 1511

2333141 for SAP S/4HANA 1610

Collection of restriction related to MFLE: 2233100

ALE generation for BAPIs: SAP Note 2232497

Extended Material Number in Suite Integration: SAP Note 2232396

Extended Material Number Display in Archived Data: SAP Note 2232391

Length of Customer and Supplier Material Number: SAP Note 2232366

Extended Material Number in LIS: SAP Note 2232362

Product Structure Browser: SAP Note 2229892

Characteristic Values in PLM: SAP Note 2229860

## Other Terms

18 digits, 40 digits
