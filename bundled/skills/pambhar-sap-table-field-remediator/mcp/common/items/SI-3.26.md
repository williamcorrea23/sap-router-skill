---
item_id: SI-3.26
title: "3.26 S4TWL - Material Type SERV"
pages: 178-182
sap_notes: [2224251, 2267247]
components: [LO-MD-MM]
objects: []
---
Application Components:LO-MD-MM

Related Notes:

| Note Type       |   Note Number | Note Description           |
|-----------------|---------------|----------------------------|
| Business Impact |       2267247 | S4TWL - Material Type SERV |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## Description

Material type "SERV" for services is introduced for Product Master in S/4HANA for simplification purposes. When you use material type SERV, some fields and departments that are irrelevant in S/4 are hidden from the screen. This gives all transactions relevant for material master, a leaner and simplified look.

The Product type SERV, as compared to the product type DIEN, has the product type group assigned (2-Services). SAP recommends that Cloud and On-Premise customers of S/4HANA use SERV over DIEN, particularly in scenarios such as lean service procurement . However, for scenarios where the subtleties of lean service procurement are not applicable, customers may use DIEN.

A new material type SERV (Service Materials) is created with reduced user departments and fields in the classical transactions: MM01/MM02/MM03.

As of SAP S/4HANA, on-premise edition 1511release changes are done as listed below:

## 1. Supported user departments :

Accounting Purchasing Basic Data Sales The selected fields are hidden only from the material type "Service Materials", however, they are supported for other material types.

## 2. Below fields/tabs are not available for SERV:

## Basic data 1

EAN/ UPC

EAN Category

Product allocation

Assign Effected vals

Matl Grp Package Matls

## Basic data 2

## Sales General/Plant

Replacement part

Availability check

Material freight grp

Shipping Data - Trans. Grp, LoadingGrp, Setup time, Proc. time, Base qty

Packaging material data - Matl Grp Pack.Matls, Maximum level, Packaging mat. Type, Stack ability factor, Allowed pkg weight, Excess wt tolerance, Allowed pkg volume, Excess volume tol., Ref. mat. for pckg, Closed

General plant parameter  - Neg. stocks, SerialNoProfile, DistProf, SerializLevel, IUID-Relevant, External Allocation of UII, IUID Type

## Purchasing

Material freight grp

Other data - GR Processing time, Post to insp. stock, Critical Part, Source list, Quota arr. usage, JIT delivery sched.

## Accounting 1

VC: Sales order stk

Price control nur Wert S

Moving price

Total Stock

Proj. stk val. Class

Total Value

Valuated Un

Accounting Previous Year (Button)

MovAvgPrice PP

Total stock

Total value PP

Std cost estimate (Button)

## Accounting 2

## Sales: Sales Org 1

X-distr. Chain status

Valid from

Dchain-spec status

Valid from

Min. dely qty

## Delivery Unit

## Sales: Sales Org 2

Matl statistics grp

Product attributes - Product attribute 1/2/3/4/5/6/7/8/9/10

As of S/4HANA 1605 CE and 1511 FPS2, additionally, the following fields are not supported for Service Materials (SERV) type:

## Basic data 1

X-plant matl status

Lab/Office

Prod. Hierarchy

Valid from

Packaging material data (entire section)

## Sales General/Plant

Qual.f.FreeGoodsDis.

## Purchasing

Qual.f.FreeGoodsDis.

## Accounting 1

ML act  indicator

## Sales: sales org. 2

Product Hierarchy

## Required and Recommended Action(s)

## Configurations required for SERV that are part of SET:

Material type SERV(Table T134, delivery class: G)

This attribute of SERV is provided by SET content

Screen sequence control(SPRO transaction: OMT3E

Table T133K 'Influencing Factors: Screen Sequence No.'  / Delivery Class: G

Tables T133S and T133T are also part of SET content

## Related SAP Notes

| General information about this Simplification Item   | SAP Note 2224251   |
|------------------------------------------------------|--------------------|

## 4. Commercial Project Management
