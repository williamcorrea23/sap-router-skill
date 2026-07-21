# Testing Scenarios Guide

This guide covers how to test the Business skill with sample data quality issues.

## Prerequisites

Start the Docker containers:

```bash
docker compose up -d
```

If you've modified `database/seed.sql`, recreate the business-db:

```bash
docker compose down business-db
docker volume rm skillian_business_db_data
docker compose up -d
```

## Test Scenario: Duplicate Transactions

**Location**: Company 1000, Period 2024012 (December 2024)

**Issue**: Delta load failure caused invoices to be loaded twice, doubling revenue.

### Expected vs Actual

| Metric | Expected | Actual (with duplicates) |
|--------|----------|--------------------------|
| Revenue | 110,000 EUR | 220,000 EUR |
| COGS | 30,000 EUR | 60,000 EUR |
| Variance vs Budget | 0% | +100% |

### Test Queries

**1. Check transaction counts**

Ask the assistant:
> "Show me FI transactions for company 1000 in December 2024"

Expected: You'll see multiple entries with the same document numbers (5000001, 5000002).

**2. Compare actual vs budget**

Ask:
> "Compare actual vs budget for company 1000 in period 012"

Expected: ~100% favorable variance due to doubled amounts.

**3. Identify duplicates by document**

Ask:
> "Show me FI summary for company 1000 period 012 grouped by document number"

Expected: Documents 5000001 and 5000002 appear with doubled amounts.

**4. Cross-source comparison**

Ask:
> "Compare FI, consolidation and BPC data for company 1000 December 2024"

Expected: All sources show the same doubled amounts (issue propagated through the pipeline).

### Verification SQL

Connect to the business database directly:

```bash
docker exec -it skillian-business-db psql -U business -d business_db
```

```sql
-- Count transactions by document
SELECT ac_docnr, COUNT(*) as occurrences, SUM(cs_trn_lc) as total
FROM fi_reporting
WHERE compcode = '1000' AND fiscper = '2024012' AND gl_acct = '4000000'
GROUP BY ac_docnr
ORDER BY ac_docnr;

-- Expected output shows doc 5000001 and 5000002 with 2 occurrences each
```

## Other Test Scenarios

### Clean Data (Jan-Mar 2024)

Periods 2024001-2024003 contain clean data for testing normal operations:
- Budget vs actual comparisons
- Intercompany transactions
- Multi-company consolidation

### Intercompany Transactions

Company 1000 sells to Company 2000 (US subsidiary):
- IC revenue in 1000: 50,000 EUR
- IC COGS in 2000: 50,000 EUR
- Elimination entries present in consolidation_mart

Test with:
> "Show intercompany transactions between company 1000 and 2000"

## Troubleshooting

**Database not responding**: Check container health
```bash
docker compose ps
docker logs skillian-business-db
```

**Data not loaded**: Verify seed file was executed
```bash
docker exec -it skillian-business-db psql -U business -d business_db -c "SELECT COUNT(*) FROM fi_reporting;"
```

**App can't connect to business-db**: Check the connector configuration in `app/config.py` and ensure the connection string points to the correct host/port.
