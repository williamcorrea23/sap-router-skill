# CAP Database Configuration Reference

**Source**: [https://cap.cloud.sap/docs/guides/databases](https://cap.cloud.sap/docs/guides/databases)

## Supported Databases

| Database | Node.js Package | Use Case |
|----------|-----------------|----------|
| SQLite | `@cap-js/sqlite` | Development, testing |
| SAP HANA | `@cap-js/hana` | Production |
| PostgreSQL | `@cap-js/postgres` | Production |

## SQLite (Development)

### Installation

```sh
npm add @cap-js/sqlite -D
```

### Configuration

```json
{
  "cds": {
    "requires": {
      "db": {
        "kind": "sqlite",
        "credentials": { "url": ":memory:" }
      }
    }
  }
}
```

### File-based SQLite

```json
{
  "cds": {
    "requires": {
      "db": {
        "kind": "sqlite",
        "credentials": { "url": "db.sqlite" }
      }
    }
  }
}
```

### Deploy Schema

```sh
cds deploy --to sqlite:db.sqlite
```

---

## SAP HANA (Production)

### Installation

```sh
npm add @cap-js/hana
cds add hana
```

### Configuration

```json
{
  "cds": {
    "requires": {
      "db": {
        "[production]": {
          "kind": "hana",
          "deploy-format": "hdbtable"
        }
      }
    }
  }
}
```

### Hybrid Development

```sh
# Add HANA for hybrid mode
cds add hana --for hybrid

# Deploy to HANA Cloud
cds deploy --to hana

# Run locally with remote HANA
cds watch --profile hybrid
```

### Build for HANA

```sh
cds build --for hana
```

Generates in `gen/db/`:
- `.hdbtable` files
- `.hdbview` files
- `.hdbtabledata` files (CSV data)
- `.hdiconfig` and `.hdinamespace`

### HANA-Specific Features

**Vector Embeddings:**
```cds
entity Documents {
  key ID : UUID;
  content : String;
  embedding : Vector(1536);  // For AI embeddings
}
```

**Geospatial:**
```cds
entity Locations {
  key ID : UUID;
  point : hana.ST_POINT;
  area : hana.ST_GEOMETRY;
}
```

### Schema Evolution

CAP handles compatible changes automatically. For incompatible changes:

```cds
@cds.persistence.journal
entity LargeTable {
  key ID : UUID;
  data : String;
}
```

Generates `.hdbmigrationtable` for manual migration control.

### Native SQL

```cds
@sql.append: 'PARTITION BY HASH (ID) PARTITIONS 4'
entity PartitionedData { ... }

@sql.prepend: 'COLUMN TABLE'
entity ColumnTable { ... }
```

---

## PostgreSQL

### Installation

```sh
npm add @cap-js/postgres
cds add postgres
```

### Configuration

> ⚠ Inline credentials below are **local-development only**. In production, never commit
> credentials to `package.json`/`.cdsrc.json` — use a service binding (`cds bind`), VCAP
> service binding, or environment variables read via CAP's standard config resolution.

```json
{
  "cds": {
    "requires": {
      "db": {
        "[development]": {
          "kind": "postgres",
          "credentials": {
            "host": "localhost",
            "port": 5432,
            "database": "mydb",
            "user": "postgres",
            "password": "postgres"
          }
        },
        "[production]": {
          "kind": "postgres"
        }
      }
    }
  }
}
```

In `[production]`, omit `credentials` — CAP picks them up from the bound service.

### Docker Development

```sh
docker run -d --name postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15
```

### Deploy Schema

```sh
cds deploy --to postgres
```

---

## Database-Agnostic Queries

All databases support standard CQL operations:

```js
// Works on all databases
await SELECT.from(Books).where({ stock: { '>': 0 } });
await INSERT.into(Books).entries({ title: 'New Book' });
await UPDATE(Books, id).set({ stock: 50 });
await DELETE.from(Books, id);
```

### Standard Functions

| Function | Description |
|----------|-------------|
| `concat(x, y)` | String concatenation |
| `contains(x, y)` | Substring check |
| `startswith(x, y)` | Prefix check |
| `endswith(x, y)` | Suffix check |
| `tolower(x)` | Lowercase |
| `toupper(x)` | Uppercase |
| `trim(x)` | Remove whitespace |
| `length(x)` | String length |
| `substring(x, i, n)` | Extract substring |

### Session Variables

```js
// Available across all databases
cds.context.user;      // Current user
cds.context.tenant;    // Current tenant
cds.context.locale;    // User locale
cds.context.timestamp; // Request timestamp
```

---

## Initial Data (CSV)

### File Location

```
db/
├── schema.cds
└── data/
    ├── my.bookshop-Books.csv
    ├── my.bookshop-Authors.csv
    └── sap.common-Countries.csv
```

### Naming Convention

`<namespace>-<EntityName>.csv` or `<namespace>.<EntityName>.csv`

### Format

```csv
ID;title;author_ID;stock;price
1;Wuthering Heights;101;100;12.99
2;Jane Eyre;102;50;10.99
```

### Test Data

Place in `test/data/` for development-only data:

```
test/
└── data/
    ├── my.bookshop-Books.csv
    └── my.bookshop-Reviews.csv
```

---

## Connection Pooling

```json
{
  "cds": {
    "requires": {
      "db": {
        "pool": {
          "min": 0,
          "max": 10,
          "acquireTimeoutMillis": 10000,
          "idleTimeoutMillis": 30000
        }
      }
    }
  }
}
```

---

## Constraints

### Not Null

```cds
entity Books {
  title : String(100) not null;
}
```

### Unique

```cds
@assert.unique: { isbn: [isbn] }
entity Books {
  isbn : String(13);
}
```

### Foreign Keys

```json
{
  "cds": {
    "features": {
      "assert_integrity": "db"
    }
  }
}
```

---

## Native Queries

> Prefer CQL whenever it can express the query. Drop to native SQL only when CQL cannot.

```js
const result = await cds.db.run(
  `SELECT * FROM my_bookshop_Books WHERE stock > ?`,
  [10]
);
```

---

## Profile-Based Configuration

```json
{
  "cds": {
    "requires": {
      "db": {
        "[development]": {
          "kind": "sqlite",
          "credentials": { "url": ":memory:" }
        },
        "[hybrid]": {
          "kind": "hana"
        },
        "[production]": {
          "kind": "hana"
        }
      }
    }
  }
}
```

### Activate Profile

```sh
# Development (default)
cds watch

# Hybrid
cds watch --profile hybrid

# Production
NODE_ENV=production cds serve
```
