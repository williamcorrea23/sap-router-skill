---
name: sap-hana-ml
description: SAP HANA Machine Learning — PAL (Predictive Analysis Library), APL (Automated Predictive Library), HANA ML Python client, built-in ML algorithms (regression, classification, clustering, time series), model training in HANA, model consumption from ABAP/CAP. Use when implementing HANA ML models, calling PAL/APL procedures, or integrating ML into ABAP applications.
trigger:
  keywords: [PAL, APL, HANA ML, machine learning, regression, classification, clustering, time series, predictive, model training]
  intent: >-
    Use when implementing HANA ML models, calling PAL/APL procedures, or integrating ML into ABAP applications.
---

# SAP HANA Machine Learning

In-database machine learning with PAL and APL libraries.

## PAL (Predictive Analysis Library)

```sql
-- Train a linear regression model
CREATE PROCEDURE TRAIN_REGRESSION()
LANGUAGE SQLSCRIPT AS
BEGIN
  CALL _SYS_AFL.PAL_LINEAR_REGRESSION(
    TRAIN_DATA => (SELECT * FROM TRAINING_DATA),
    PARAMETERS => '{"THREAD_NUMBER":4}',
    MODEL => RESULT_MODEL,
    STATISTICS => RESULT_STATS
  );
  INSERT INTO MODEL_TABLE SELECT * FROM :RESULT_MODEL;
END;
```

## APL (Automated Predictive Library)

```sql
-- Automated model selection
CALL _SYS_AFL.APL_FORECAST(
  INPUT => (SELECT * FROM SALES_DATA),
  PARAMETERS => '{
    "HORIZON": 12,
    "TARGET": "sales_amount",
    "DATE_COLUMN": "posting_date",
    "GRANULARITY": "MONTH",
    "LAST_TRAINING_DATE": "2026-01-01"
  }',
  RESULT => FORECAST_RESULT
);
SELECT * FROM :FORECAST_RESULT;
```

## HANA ML Python Client

```python
from hana_ml import dataframe
from hana_ml.algorithms.pal import linear_regression

# Connect
conn = dataframe.ConnectionContext(
    address='my-hana.cfapps.us10.hana.ondemand.com',
    port=443, user='SYSTEM', password='...', encrypt=True
)

# Load data
df = conn.table('TRAINING_DATA', schema='ZSALES').select(['X1','X2','Y']).collect()

# Train model
lr = linear_regression.LinearRegression()
lr.fit(data=df, key='ID', features=['X1','X2'], label='Y')

# Predict
predictions = lr.predict(data=conn.table('PRODUCTION_DATA'))
conn.create_table(predictions, 'PREDICTIONS')
```

## Integration with ABAP

```abap
" Call HANA ML procedure from ABAP via ADBC
DATA(lo_sql) = NEW cl_sql_statement( ).
lo_sql->execute_ddl(
  |CALL ZSP_REGRESSION_PREDICT( iv_model_name = 'LREG_001', |
  & |iv_input_table = 'Z_NEW_DATA', iv_output_table = 'Z_PREDICTIONS' )|
).
```

## Available Algorithms

| Category | PAL Algorithms | APL Algorithms |
|---|---|---|
| Classification | SVM, Decision Tree, Random Forest, Naive Bayes | Automated classifier |
| Regression | Linear, Polynomial, GLM, Exponential | Automated regression |
| Clustering | K-Means, DBSCAN, Agglomerative | — |
| Time Series | ARIMA, Exponential Smoothing, Croston | Automated forecasting |
| Association | Apriori, FP-Growth | — |
| Recommendation | ALS (Collaborative Filtering) | — |

## Gotchas
- PAL requires `_SYS_AFL` schema privilege
- Model training is CPU-intensive — use dedicated HANA worker threads
- Python client needs `hana_ml` pip package + HANA ODBC driver
- APL auto-selects best algorithm — use PAL when you need specific algorithm control
