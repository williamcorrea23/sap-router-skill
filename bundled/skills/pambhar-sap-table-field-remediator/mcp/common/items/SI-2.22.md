---
item_id: SI-2.22
title: "2.22 S4TWL - Side Panel functionality in SAP S/4HANA (on-premise)"
pages: 55-58
sap_notes: [2340424]
components: [FI]
objects: []
---
## Application Components:FI

Related Notes:

| Note Type       |   Note Number | Note Description                                    |
|-----------------|---------------|-----------------------------------------------------|
| Business Impact |       2340424 | Availability of Side Panels in S/4HANA (on-premise) |

## Symptom

You are doing a system conversion to SAP S/4HANA (on-premise). You use Side Panels in the SAP Business Client and would like to understand the conversion behavior.

## Reason and Prerequisites

SAP S/4HANA (on-premise) comes with a new UI product. The S/4HANA (on-premise) UI product is not the successor of any Business Suite product and delivers a set of applications which is from a technical and scope perspective independent from any previous Business Suite UI product. The SAP Business Client Side Panel functionality is available in S/4HANA (on-premise). Some of the Business Suite Side Panel CHIPs  (Collaborative Human Interface Part) are no longer available in S/4HANA and the delivered CHIP catalog is adjusted accordingly.

A CHIP (Collaborative Human Interface Part) is an encapsulated piece of software used to provide functions in collaboration with other CHIPs in a Web Dynpro ABAP Page Builder page or side panel. All available CHIPs are registered in a library (CHIP catalog). From a technical point of view, CHIPs are Web Dynpro ABAP components that implement a specific Web Dynpro component interface.

## More information is available

at:  http://help.sap.com/erp2005_ehp_07/helpdata/en/f2/f8478f40ca420991a72eed8f222c 8d/content.htm?current_toc=/en/58/327666e82b47fd83db69eddce954bd/plain.htm

## Solution

The new program paradigm in S/4HANA and the consumption of functionality via SAP Fiori results in an adjustment of the delivered CHIP catalog for the SAP Business Client Side Panel functionality.

The following SAP Business Client Side Panel CHIPs are no longer available:

| CHIP Name                    | CHIP                                                                               |
|------------------------------|------------------------------------------------------------------------------------|
| BSSP_LPD_FI_AP               | Accounts Payable Reporting (Links)                                                 |
| BSSP_LPD_FI_AR               | Accounts Receivable Reporting (Links)                                              |
| BSSP_LPD_FI_AA               | Asset Accounting Reporting (Links)                                                 |
| BSSP_LPD_CO_OM_CCA           | Cost Center Reporting (Links)                                                      |
| BSSP_LPD_FI_GL               | General Ledger Reporting (Links)                                                   |
| BSSP_LPD_CO_OM_OPA           | Internal Order Reporting (Links)                                                   |
| BSSP_LPD_PM_OM_OPA           | Maintenance / Service Order Reporting (Links)                                      |
| BSSP_LPD_CO_PC               | Product Cost Reporting (Links)                                                     |
| BSSP_LPD_FI_GL_PRCTR         | Profit Center Reporting (Links)                                                    |
| BSSP_FI_AA_POSTED_DEPREC     | Asset Accounting: Posted Depreciation (Reports (Display as Form / List))           |
| BSSP_CO_OM_CC_ACT_PLAN_AGGR  | Cost Center: Cumulative Actual/Planned Costs (Reports (Display as Form / List))    |
| BSSP_FI_AR_TOTALS            | Cost Center Balance: Totals (Reports (Display as Form / List))                     |
| BSSP_FI_AR_DUE_ANALYSIS      | Customer Due Date Analysis (Reports (Display as Form / List))                      |
| BSSP_FI_AR_DUE_FORECAST      | Customer Due Date Forecast (Reports (Display as Form / List))                      |
| BSSP_FI_AR_OVERDUE           | Customer Overdue Analysis (Reports (Display as Form / List))                       |
| BSSP_CO_OM_IO_ACT_PLAN_AGGR  | Internal Order: Cumulative Actual/Planned Costs (Reports (Display as Form / List)) |
| BSSP_CO_PC_MAT_ACT_PLAN_AGGR | Material: Aggregated Actual / Planned Costs (Reports (Display as Form / List))     |
| BSSP_GR_IR_GOODS_RECEIPT     | Purchase Order History: Goods Receipt (Reports (Display as Form / List))           |
| BSSP_GR_IR_INVOICE_RECEIPT   | Purchase Order History: Invoice Receipt(Reports (Display as Form / List))          |
| BSSP_GR_IR_OPEN_ITEM         | Purchase Order: Open Items (Reports (Display as Form / List))                      |
| BSSP_FI_AP_TOTALS            | Vendor Balance Totals (Reports (Display as Form / List))                           |
| BSSP_FI_AP_DUE_ANALYSIS      | Vendor Due Date Analysis (Reports (Display as Form / List))                        |
| BSSP_FI_AP_DUE_FORECAST      | Vendor Due Date Forecast (Reports (Display as Form / List))                        |
| BSSP_FI_AP_OVERDUE           | Vendor Overdue Analysis (Reports (Display as Form / List))                         |

The following SAP Business Client Side Panel CHIPs are no longer available:

| BSSP_FI_AA_POSTED_DEPREC_C     | Asset Accounting: Posted Depreciation (Reports (Display as Chart))                       |
|--------------------------------|------------------------------------------------------------------------------------------|
| BSSP_CO_OM_CC_PERIOD_BD_C      | Cost Center: Breakdown Actual/Planned Costs by Period (Reports (Display as Chart))       |
| BSSP_CO_OM_CC_ACT_PLAN_AGGR_C  | Cost Center: Cumulative Actual/Planned Costs (Reports (Display as Chart))                |
| BSSP_FI_AR_PERIOD_C            | Customer Balance: Period Drilldown (Reports (Display as Chart))                          |
| BSSP_FI_AR_TOTALS_C            | Customer Balance: Totals (Reports (Display as Chart))                                    |
| BSSP_FI_AR_DUE_ANALYSIS_C      | Customer Due Date Analysis (Reports (Display as Chart))                                  |
| BSSP_FI_AR_DUE_FORECAST_C      | Customer Due Date Forecast (Reports (Display as Chart))                                  |
| BSSP_FI_AR_OVERDUE_C           | Customer Overdue Analysis (Reports (Display as Chart))                                   |
| BSSP_FI_GL_ACC_BALANCE_C       | G/L Account Balance (Reports (Display as Chart))                                         |
| BSSP_CO_OM_IO_PERIOD_BD_C      | Internal Order: Actual/Planned Costs by Period (Reports (Display as Chart))              |
| BSSP_CO_OM_IO_ACT_PLAN_AGGR_C  | Internal Order: Cumulative Actual/Planned Costs (Reports (Display as Chart))             |
| BSSP_CO_PC_MAT_ACT_PLAN_AGGR_C | Material: Aggregated Actual / Planned Costs (Reports (Display as Chart))                 |
| BSSP_CO_PC_MAT_PERIOD_BD_C     | Material: Breakdown Actual/Planned Costs by Period (Reports (Display as Chart))          |
| BSSP_FI_AP_PERIOD_C            | Vendor Balance: Period Drilldown (Reports (Display as Chart))                            |
| BSSP_FI_AP_TOTALS_C            | Vendor Balance Totals (Reports (Display as Chart))                                       |
| BSSP_FI_AP_DUE_ANALYSIS_C      | Vendor Due Date Analysis (Reports (Display as Chart))                                    |
| BSSP_FI_AP_DUE_FORECAST_C      | Vendor Due Date Forecast (Reports (Display as Chart))                                    |
| BSSP_FI_AP_OVERDUE_C           | Vendor Overdue Analysis (Reports (Display as Chart))                                     |
| BSSP_FI_AA_POSTED_DEPREC_C2    | Asset Accounting: Posted Depreciation (Reports (Display as HTML5 Chart))                 |
| BSSP_CO_OM_CC_PERIOD_BD_C2     | Cost Center: Breakdown Actual/Planned Costs by Period (Reports (Display as HTML5 Chart)) |
| BSSP_CO_OM_CC_ACT_PLAN_AGGR_C2 | Cost Center: Cumulative Actual/Planned Costs (Reports (Display as HTML5 Chart))          |
| BSSP_FI_AR_PERIOD_C2           | Customer Balance: Period Drilldown (Reports (Display as HTML5 Chart))                    |
| BSSP_FI_AR_TOTALS_C2           | Customer Balance: Totals (Reports (Display as HTML5 Chart))                              |
| BSSP_FI_AR_DUE_ANALYSIS_C2     | Customer Due Date Analysis (Reports (Display as HTML5 Chart))                            |

| BSSP_FI_AR_DUE_FORECAST_C2     | Customer Due Date Forecast (Reports (Display as HTML5 Chart))                         |
|--------------------------------|---------------------------------------------------------------------------------------|
| BSSP_FI_AR_OVERDUE_C2          | Customer Overdue Analysis (Reports (Display as HTML5 Chart))                          |
| BSSP_FI_GL_ACC_BALANCE_C2      | G/L Account Balance (Reports (Display as HTML5 Chart))                                |
| BSSP_CO_OM_IO_PERIOD_BD_C2     | Internal Order: Actual/Planned Costs by Period (Reports (Display as HTML5 Chart))     |
| BSSP_CO_OM_IO_ACT_PLAN_AGGR_C2 | Internal Order: Cumulative Actual/Planned Costs (Reports (Display as HTML5 Chart))    |
| BSSP_CO_PC_MAT_ACT_PLANAGGR_C2 | Material: Aggregated Actual / Planned Costs (Reports (Display as HTML5 Chart))        |
| BSSP_CO_PC_MAT_PERIOD_BD_C2    | Material: Breakdown Actual/Planned Costs by Period (Reports (Display as HTML5 Chart)) |
| BSSP_FI_AP_PERIOD_C2           | Vendor Balance: Period Drilldown (Reports (Display as HTML5 Chart))                   |
| BSSP_FI_AP_TOTALS_C2           | Vendor Balance Totals (Reports (Display as HTML5 Chart))                              |
| BSSP_FI_AP_DUE_ANALYSIS_C2     | Vendor Due Date Analysis (Reports (Display as HTML5 Chart))                           |
| BSSP_FI_AP_DUE_FORECAST_C2     | Vendor Due Date Forecast (Reports (Display as HTML5 Chart))                           |
| BSSP_FI_AP_OVERDUE_C2          | Vendor Overdue Analysis (Reports (Display as HTML5 Chart))                            |

## Other Terms

CHIPs, Side Panel for Business Suite, S/4HANA (on-premise), Conversion
