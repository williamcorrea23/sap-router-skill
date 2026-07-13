---
name: sap-hana-cli
description: SAP HANA CLI and Database Explorer — hdbsql command-line tool, HANA Database Explorer in BAS, SQL console, catalog browser, security manager, trace configuration, backup management. Use when accessing HANA via command line, running SQL queries against HANA, or managing HANA database artifacts.
trigger:
  keywords: [hana, cli, hdbsql, database-explorer, sql, catalog, security, trace, backup, command-line]
  intent: >-
    Access and manage SAP HANA databases via command-line tools, Database Explorer, SQL console, and administration utilities.
---

# SAP HANA CLI and Database Explorer

Command-line and browser-based tools for HANA database operations.

## hdbsql CLI

```bash
# Interactive mode
hdbsql -n <host>:<port> -u <user> -p <password>

# Execute SQL file
hdbsql -n localhost:30015 -u SYSTEM -p Passw0rd -I my_script.sql

# Query from command line
hdbsql -n localhost:30015 -u SYSTEM -p Passw0rd \
  "SELECT * FROM MARA WHERE MATNR = 'MAT001'"

# Export CSV
hdbsql -n localhost:30015 -u SYSTEM -p Passw0rd \
  -o output.csv -c ";" \
  "SELECT * FROM MARA"
```

## HANA Database Explorer (BAS)

```
BTP → Dev Space → SAP HANA Database Explorer
├── Catalog Browser — Tables, Views, Procedures
├── SQL Console — Execute SQL queries
├── Security Manager — Users, Roles, Privileges
├── Trace Configuration — SQL traces, performance
└── Data Preview — Browse table contents
```

## SQL Console Tips

```sql
-- Execute with F8
-- Use : for parameter substitution
SELECT * FROM MARA WHERE MATNR = :matnr;

-- Explain plan (Ctrl+Shift+X)
SELECT * FROM MARA WHERE MATNR = 'MAT001';

-- View execution plan in Plan Visualizer tab
```

## Backup and Recovery

```bash
# Backup via hdbsql
hdbsql -n localhost:30015 -u SYSTEM -p Passw0rd \
  "BACKUP DATA USING FILE ('/backup/hana_backup')"

# Recovery
hdbsql -n localhost:30015 -u SYSTEM -p Passw0rd \
  "RECOVER DATA USING FILE ('/backup/hana_backup')"
```

## Gotchas
- Port 30015 for single-tenant; 30013 for multi-tenant (system DB)
- HANA DB Explorer only available in BAS dev spaces with HANA tools extension
- hdbsql on Windows may need full path: C:\Program Files\sap\hdbclient\hdbsql.exe
- Password visible in hdbsql command line — use secure storage instead
