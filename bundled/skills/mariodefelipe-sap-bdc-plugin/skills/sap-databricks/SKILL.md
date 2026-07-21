---
name: sap-databricks
description: Use when the user is working with SAP Databricks — setting up the account, administering workspaces, managing identity (users/groups/service principals/SCIM), configuring networking/security (IP lists, serverless egress), building notebooks, working with AI/ML (Genie, AI Functions, model serving, vector search), tracking billing/budget policies, sharing data from Databricks to BDC or from BDC into Databricks, or using the REST API. Trigger phrases include "SAP Databricks", "Databricks workspace", "Databricks admin", "Databricks identity", "SCIM Databricks", "Databricks notebook", "Databricks billing", "serverless budget", "Databricks API", "share to BDC", "publish to BDC Databricks", "mount BDC data".
---

# SAP Databricks

## Overview

SAP Databricks is a special edition of Databricks available as an application within SAP Business Data Cloud. It provides advanced AI and analytics capabilities fully integrated with your SAP landscape. Key benefits include pre-configured Delta Sharing access to BDC data products without replication, ability to combine SAP data with external data and publish results back to BDC, fully managed serverless compute and storage, and instant provisioning from SAP for Me with integrated SSO.

**Key use cases:** automated forecasting (time-series with automatic algorithm/hyperparameter selection), fine-tuning LLMs with your data, exploratory data analysis with collaborative multi-language notebooks, business intelligence with SQL editor and visualizations.

**Supported regions:** AWS (ap-northeast-1, ap-southeast-1, ap-southeast-2, ca-central-1, eu-central-1, us-east-1), GCP (asia-south1, europe-west3, us-central1), Azure (eastus, westeurope, westus2). Accounts can only deploy workspaces in a single region.

---

## Setup & Accounts

### Provisioning from SAP for Me
1. Follow SAP documentation to provision SAP Databricks from the SAP for Me portal.
2. Verify email and agree to terms in the Databricks sign-up flow.
3. The first user added becomes the initial account admin and receives an email when ready.
4. A first workspace is automatically created.

### Initial Configuration
- (Optional) Configure network settings for enhanced security.
- Add users and groups manually or via SAP Cloud Identity Service Identity Provisioning (SCIM integration).
- Users log in at `login.databricks.com` with SSO credentials.

### Creating Additional Workspaces
From the account console **Workspaces** tab:
1. Click **Create workspace**.
2. Enter workspace name and select region.
3. Click **Create**.
4. Assign users/groups permissions on the **Permissions** tab using **Add permissions**.

**Note:** Accounts can only deploy workspaces in a single region.

---

## Admin Roles & Responsibilities

### Account Admin
- Create and manage workspaces
- Configure networking controls and IP access lists
- Manage users, groups, and service principals at account level
- Assign metastore privileges and admin roles
- Access account console at `accounts.cloud.databricks.com` or via workspace selector → **Manage account**
- Transfer account owner role (contact Databricks support if needed)

### Workspace Admin
- Manage access control for workspace objects (notebooks, queries)
- Create and manage serverless SQL warehouses
- Manage workspace identities and admin settings
- Access system tables and audit logs
- Create external location connections to cloud storage (S3, Azure, GCS)
- Access workspace settings via username menu → **Settings**
- Create and manage serverless budget policies
- Manage metastore permissions (workspace-bound catalog)

### Metastore Admin
- CREATE CATALOG — create catalogs in metastore
- CREATE EXTERNAL LOCATION — create external locations
- CREATE STORAGE CREDENTIAL — create storage credentials
- CREATE SHARE and CREATE PROVIDER — for Delta Sharing
- **Must not** disable Delta Sharing, remove metastore root storage, remove workspaces, create/delete metastores, or modify Delta Sharing token lifetime (storage managed by SAP)

---

## Identity & Permissions

### Identity Types
- **Users:** Recognized by email address, synchronized via SAP Cloud Identity Services Identity Provisioning (SCIM).
- **Groups:** Collections of identities for managing access to workspaces, data, and securable objects.
- **Service principals:** Identities for jobs, automated tools, scripts, apps, CI/CD platforms.

Account limit: 10,000 combined users/service principals, 5,000 groups.

### User Management & Provisioning
- **Recommended:** Use SAP Cloud Identity Services as single source of truth for user provisioning.
- Account admins can add users manually who weren't synced via SCIM.
- Create users one-by-one or import via CSV.
- Delete/deactivate users through SAP Cloud Identity Services documentation.
- Perform **Resync Provisioning Job** to synchronize users/groups between SAP Cloud Identity Services and SAP Databricks account.

### Access Control Models

**Workspace object access control (ACLs):**
- Workspace admins have CAN MANAGE permission on all workspace objects.
- Users automatically own CAN MANAGE permission for objects they create.
- Configure permissions via access control lists.

**Data access control (Unity Catalog):**
- Access governed by Unity Catalog securable objects.
- Each securable object has an owner (can manage permissions).
- Admins manage object permissions.
- SAP Databricks users must have **USE PROVIDER privilege** to access SAP BDC data products.

### Admin Role Assignment
- **Account admins:** Assign other account admins.
- **Workspace admins:** Determined by membership in **workspace admins** group (default, cannot be deleted).
- Both can assign workspace admins.

### Group Management
- **Group managers:** Manage group membership, delete group, assign group manager role to others.
- Account admins have group manager role on all groups.
- Workspace admins have group manager role on account groups they create.

### Service Principals
- **Service principal managers:** Manage service principal roles.
- Account admins have service principal manager role on all service principals.
- Workspace admins have service principal manager role on service principals they create.

---

## Networking & Security

### Authentication
- Managed via SAP Cloud Identity Services.
- Users provisioned via SCIM from Identity Provisioning.
- No password support — single sign-on only.
- All users created in SAP Cloud Identity Services synchronized bidirectionally with SAP Databricks.

### IP Access Lists (IP Allowlisting)
- Restrict access to account and workspaces by user IP address.
- By default, users can connect from any IP.
- Reference **SAP network access gateways** before enforcing IP ACLs to avoid breaking BDC connection.
- Manage via Databricks documentation "Manage IP access lists".

### Serverless Egress Control
- Manage outbound network connections from serverless compute resources.
- Reduce risk of data exfiltration.
- **Warning:** Check serverless egress configuration before enforcing to avoid breaking BDC connection.
- See Databricks documentation "What is serverless egress control?".

### Network Connectivity Configuration (NCC)
- Account-level constructs for firewall enablement at scale.
- Enable access from Databricks to external network sources.
- Available for AWS and Azure deployments.
- See Databricks docs "Configure a firewall for AWS/Azure deployments".

### Data Encryption
- Data stored in Unity-governed storage backed by SAP HANA Cloud Data Lake (SAP-managed, not customer-configurable).
- Data in motion protected by mTLS-based transport encryption.
- Compute storage (temporary data, notebook results) protected by customer-specific encryption key managed by SAP.

### Backup & Recovery
- Data automatically backed up with 14-day snapshot retention (adds to storage size).
- If data overwritten/deleted, retained in snapshot for 14 days.
- **Recovery:** Submit case to SAP Support.
- **Notebooks/source code:** Not backed up if workspace deleted — **use connected Git repositories**.

### Enhanced Security & Compliance Add-on
- Controls for regulated industries.
- See compliance controls for AWS, GCP, Azure deployments.

---

## Notebooks & Data Analysis

### Notebook Features
- Web-based code editor for interactive data analysis.
- Supports **Python and SQL** (default language is most recently used).
- Real-time coauthoring, automatic versioning, built-in visualizations.
- Markdown for embedded links, images, commentary.

### Creating & Editing Notebooks
1. Click **+ New** in left sidebar → **Notebook**.
2. Databricks creates blank notebook in default folder.
3. Attach to compute resource via dropdown menu.

### Serverless Compute
- Click compute dropdown → **Serverless** to attach on-demand computing.
- Connect to serverless SQL warehouses.

### Importing SAP Data
- Active SAP data products mounted to catalogs in Unity Catalog.
- Query requires READ access to catalog and schema.
- Example: `SELECT * FROM sap_data.cashflow.cashflowforecast`

### Visualizations
1. Run cell with tabular results.
2. Click **+** above result → **Visualization**.
3. Choose visualization type (chart, etc.).
4. Customize properties, column selection, grouping.
5. Click **Save**.

### Debugging
- **Python only:** Built-in interactive debugger (breakpoints, step-execution, variable inspection).
- Enable via username → **Settings** → **Developer** → toggle **Python Notebook Interactive Debugger**.

### Scheduling Notebooks
- Create and manage notebook jobs directly in UI.
- Create job and schedule via **Schedule a notebook** if not already assigned.

### Git Folders
- Visual Git client and API in Databricks.
- Support cloning, committing, pushing, pulling, branch management, diff comparison.
- Develop notebooks/files with Git version control for CI/CD.

### Genie Code
- Context-aware AI assistant for data and code.
- Available in SQL editor and notebooks.
- Features: AI autocomplete, natural language data filtering, error diagnosis, quick-fix suggestions.

### Web Terminal
- Interactive shell command execution (if enabled by account admin).
- Useful for batch operations on multiple files.
- Launch from notebook (serverless compute environment 2) via terminal icon in right sidebar.

---

## AI & Machine Learning

### Mosaic AI Platform
Unifies AI lifecycle from data collection/preparation to model development/LLMOps to serving/monitoring.

### Features Available

**AI Playground:** Chat-like environment to test, prompt, and compare supported LLMs.

**AI Functions:** Built-in functions to apply AI (text translation, sentiment analysis, etc.) on Databricks data. Run from notebook or SQL editor.

**Mosaic AI Gateway:** Centralized service for governing, monitoring, and managing access to generative AI models and model serving endpoints. Provides governance, monitoring, production readiness, secure traffic management.

**Mosaic AI Model Serving:** Deploy, govern, and query AI models for real-time/batch inference. Each served model available as REST API. Configure for generative AI (foundation models, third-party models).

**Mosaic AI Vector Search:** Vector database for embedding vectors, automatic knowledge base sync. Built-in to Databricks, integrated with governance and productivity tools. Use for RAG, recommendation systems, image recognition.

**Lakehouse Monitoring:** Monitor statistical properties and data quality across tables. Track ML model performance and drift via inference tables with automatic payload logging.

**Managed MLflow:** Open-source AI engineering platform for agents, LLMs, ML models. Debug, evaluate, monitor, optimize production AI apps. Experiment tracking, evaluation, model registry, deployment.

**Mosaic AI Agent Framework:** Tools for building, deploying, evaluating production-quality agents (RAG apps). Compatible with LangChain, LlamaIndex. Leverage Databricks managed Unity Catalog and Agent Evaluation.

**Mosaic AI Agent Evaluation:** Evaluate quality, cost, latency of agentic AI applications (RAG, chains). Identify issues and root causes across development, staging, production phases. Metrics logged to MLflow Runs.

**AutoML Forecasting:** Automatically select best algorithm and hyperparameters for time-series data on fully-managed compute.

**Foundation Model Fine-tuning:** Customize foundation models with your data. Requires supported region (us-east-1). Less data, time, compute than training from scratch.

**Unity Catalog:** Manage AI assets (models, experiments). Centralized governance, lineage tracking, data/model monitoring.

### AI Assets in Unity Catalog
All data assets and ML artifacts (models, functions) discoverable and governed in single catalog. Track lineage from raw data to production model. Built-in monitoring saves quality metrics to tables.

---

## External Data & Delta Sharing

### Connect to Cloud Storage (Read-Only)

**S3 (AWS):** Create external locations to AWS S3 bucket (admin only). Must be read-only to prevent data loss.

**Azure Blob Storage:** Create external locations to Azure blob storage/Data Lake Storage (admin only). Must be read-only.

**GCS (GCP):** Create external locations to Google Cloud Storage bucket (admin only). Must be read-only.

### Delta Sharing
- Receive Delta Sharing shares from workspaces inside/outside account.
- SAP Databricks accounts are **recipients only**; cannot initiate shares outside SAP.

---

## Publishing to BDC

### Pre-configured Delta Sharing to BDC
- Each workspace pre-populated with Delta Sharing recipient **sap-business-data-cloud**.
- Allows sharing data from SAP Databricks back to SAP BDC.

### Create & Publish a Share
1. Create share via Catalog Explorer, SQL, or CLI.
2. Add data to share.
3. Click **Share data**.

### Semantic Metadata
- Enrich shared data for discovery in SAP BDC.
- Use SAP BDC SDK to describe data using **CSN and ORD**.

---

## Receiving SAP Data into Databricks

### Delta Sharing from SAP BDC
- Each SAP application automatically appears as provider in SAP Databricks account.
- Activating data product in SAP BDC automatically creates Delta Share to SAP Databricks.
- Data products mounted to catalogs available in notebooks, SQL editor, AI/ML products.

### Make SAP Data Available
- Requires **USE PROVIDER** and **CREATE CATALOG** metastore permissions.
- From Catalog Explorer:
  1. Click **Catalog**.
  2. Click **Delta Sharing**.
  3. Click SAP provider.
  4. Click **Mount to catalog** for target table.
  5. Create new catalog or mount to existing.

### SAP Semantic Metadata
- Automatically ingested into Unity Catalog at table level when accessed.
- Metadata synced from SAP BDC includes:
  - **Table/column comments:** Purpose descriptions.
  - **Primary keys:** Synced as Unity Catalog primary key constraints.
  - **Foreign keys:** Relationships within same share (cross-share not supported).
  - **SAP governance tags:** System tags in `sap.PersonalData.*` namespace classifying personal/sensitive data.

### SAP Governance Tags (Read-Only)
- Tags in `sap.PersonalData` namespace synced as system governed tags.
- **Do not manually assign/modify/delete** tags in `sap.*` namespace (system-reserved).

Synced tags:
- `@PersonalData.entitySemantics` → `sap.PersonalData.entitySemantics` (table level): DATA_SUBJECT, DATA_SUBJECT_DETAILS, OTHER.
- `@PersonalData.fieldSemantics` → `sap.PersonalData.fieldSemantics` (column level): DATA_SUBJECT_ID, CONSENT_ID, etc.
- `@PersonalData.isPotentiallyPersonal` → `sap.PersonalData.isPotentiallyPersonal` (column level): true/false.
- `@PersonalData.isPotentiallySensitive` → `sap.PersonalData.isPotentiallySensitive` (column level): true/false.

### Using SAP BDC Metadata in Databricks
- **Catalog Explorer:** View comments, key constraints, tags in table/column details. Filter by comment content.
- **SQL:** Use `DESCRIBE TABLE EXTENDED` for comments/constraints. Query `INFORMATION_SCHEMA.TABLE_TAGS` for governance tags.
- **Genie:** Ask natural language questions in Genie spaces with SAP BDC tables without understanding SAP naming conventions.
- **Governance:** Use synced SAP tags in ABAC policies to control access to sensitive data.
- **Audit logs:** Metadata sync events (tag assignments, comment updates, constraints) recorded in audit logs.

---

## Billing & Budget Policies

### Billable Usage System Table
- Path: `system.billing.usage`
- Contains account-wide billable usage data (read-only).
- Grant USE and SELECT permissions to users (requires metastore admin + account admin).

**Key columns:**
- `record_id` (string): Unique ID.
- `account_id` (string): Account ID.
- `workspace_id` (string): Workspace ID.
- `sku_name` (string): SKU name (e.g., ENTERPRISE_SAP_ALL_PURPOSE_SERVERLESS_COMPUTE_EUROPE_FRANKFURT).
- `cloud` (string): AWS, AZURE, GCP.
- `usage_start_time`, `usage_end_time` (timestamp): UTC+0 timezone.
- `usage_date` (date): For faster date aggregation.
- `custom_tags` (map): Custom tags from serverless budget policy.
- `usage_unit` (string): Unit (e.g., DBU).
- `usage_quantity` (decimal): Units consumed.
- `usage_metadata` (struct): Compute/job IDs.
- `identity_metadata` (struct): Identity info.
- `record_type` (string): ORIGINAL, retraction, or restatement.

### SKU Pricing Table
- Path: `system.billing.list_prices`
- Historical log of SKU pricing (read-only).
- Record added each time SKU price changes.

### Capacity Unit Estimation
- Use SAP Business Data Cloud Capacity Unit Estimator.
- Search for **Capacity Units - SAP Business Data Cloud (CY475)** and **Capacity Units – SAP Databricks (CY477)**.

### Serverless Budget Policies
- **Preview feature** for cost attribution via tags on serverless compute workloads.
- Tags applied to activity by users assigned policy, logged in billing records.
- Attribute usage to specific users, groups, projects.

**Permissions:**
- **Creator:** Workspace admin.
- **User:** Select policy when creating notebook/serving endpoint.
- **Manager:** Use policy, edit definitions/permissions.

**Create a policy:**
1. Click username → **Settings** → **Compute**.
2. Next to **Serverless budget policies**, click **Manage**.
3. Click **Create**.
4. Add name and tags → **Create**.

**Manage permissions:**
- Policy's **Permissions** tab → **Grant access**.
- Assign user/group/service principal → Select role (User/Manager) → **Save**.

**Policy assignment:**
- Single policy: Auto-applied to new resources.
- Multiple policies: User must select on creation.
- No selection: Defaults to first alphabetically.
- Apply via notebook **Environment** panel, job, or serving endpoint creation.

**Billing integration:**
- Tags propagate to `system.billing.usage` custom_tags column.
- If notebook run as job, job's policy applied (not notebook's).
- Policy changes apply only to usage after update.

---

## API Reference

### Authentication
All workspace and account APIs require authentication via Databricks REST API (see Databricks REST API Introduction).

### Workspace-Level APIs

**Databricks Workspace:** Git credentials, repos, secrets, workspace object management, file operations.

**Machine Learning:**
- **Experiments:** Create/delete/list, run management, logged models, tags, tracing.
- **Model Registry:** Model versions, stages, comments, webhooks, transition requests.
- **Real-time Serving:** Serving endpoints (CRUD, tags, rate limits, logs), query endpoints.
- **Vector Search:** Endpoints (CRUD, budget policy), indexes (CRUD, query, scan, sync, upsert).

**Identity & Access Management:**
- **Current User:** `GET /api/2.1/me` — get current user info.
- **Groups:** List, get, replace, update groups.
- **Service Principals:** List, get, replace, update, delete.
- **Users:** List, get, replace, update.
- **Permissions:** Get/set/update object permissions, get permission levels.

**Databricks SQL:**
- **Statement Execution:** Execute, get status/manifest/results, cancel, get chunks.
- **SQL Warehouses:** CRUD, start, stop, permissions.
- **Queries:** CRUD (preview).
- **Query History:** List queries.

**Unity Catalog:**
- **Artifact Allowlists:** Get/set.
- **Catalogs:** CRUD.
- **Credentials:** CRUD, validate, generate temporary credentials.
- **External Locations:** Get, create, update, delete.
- **Functions:** CRUD.
- **Grants:** Get effective/explicit permissions, update.
- **Metastores:** Get summary, get, list metastore assignments.
- **Model Versions:** Get by alias, list, CRUD.
- **Online Tables:** CRUD (preview).
- **Quality Monitors:** CRUD, queue refresh, get refresh.
- **Registered Models:** CRUD, set aliases, delete aliases.
- **Resource Quotas:** List, get.
- **Schemas:** CRUD.
- **Storage Credentials:** CRUD, validate.
- **System Schemas:** List, enable, disable (preview).
- **Table Constraints:** Create, delete.
- **Tables:** List, get, delete, existence check.
- **Temporary Table Credentials:** Generate.
- **Volumes:** CRUD.
- **Workspace Bindings:** Get, update.

### Account-Level APIs
Contact Databricks for available account-level APIs not covered above.

---

## Admin Best Practices

### Data Governance
- Unity Catalog provides centralized access control, auditing, lineage, data discovery.
- See Databricks data processing agreement for compliance controls.

### Default Workspace Catalog
- Every workspace includes workspace catalog named after workspace.
- All workspace users can create assets in default schema.
- Default catalog workspace-bound (accessible only through workspace).

### SAP Data Access
- SAP BDC data products automatically added to catalog in SAP Databricks.
- Default: All workspace users have read-only access to shared schemas/tables.
- Admins manage user/group permissions via Unity Catalog privilege model.
- **Best practice:** Mark all external locations and storage credentials as read-only to keep SAP data within SAP-managed storage.

### Workspace Creation Strategy
- Create separate workspaces for different development stages (dev, test, prod) or teams.
- All SAP Databricks workspaces are serverless (storage/compute managed).
- Single region per account limit.

### Identity Management Best Practices
- Use **SAP Cloud Identity Services as single source of truth** for users.
- Passwords not supported — SSO only.
- **Organize users into account-level groups**, assign workspace/access-control policies to groups, not individuals.
- Add SCIM-synchronized groups to account groups.
- Regularly resync provisioning to ensure accuracy.

### Usage Monitoring
- Create serverless budget policies for cost attribution at granular level.
- Enforce cost attribution tags on serverless compute workloads.
- Access billable usage at `system.billing.usage`.
- View SKU pricing at `system.billing.list_prices`.

### Metastore Management
- Workspace admins have catalog admin privileges on workspace-bound catalog by default.
- Account admins can assign metastore admin roles.
- **Restrictions:** Metastore admins must not disable Delta Sharing, remove/change root storage, remove workspaces, create/delete metastores, or modify Delta Sharing token lifetime.

### Networking Best Practices
- Use IP access lists to restrict account/workspace access by IP.
- Configure serverless egress control to manage outbound connections and reduce data exfiltration risk.
- Use network connectivity configurations (AWS/Azure) for firewall management at scale.
- **Before enforcing IP ACLs or serverless egress:** Check SAP network access gateways to avoid breaking BDC connection.

---

## References
- `references/sapDatabricks.pdf` — SAP Databricks overview and features
- `references/SAPDatabricks/Set up your SAP Databricks account _ SAP Databricks.pdf` — Account provisioning and workspace creation
- `references/SAPDatabricks/SAP Databricks admin guide _ SAP Databricks.pdf` — Admin roles and responsibilities
- `references/SAPDatabricks/SAP Databricks admin best practices _ SAP Databricks.pdf` — Best practices for governance, security, cost management
- `references/SAPDatabricks/Identity management and permissions _ SAP Databricks.pdf` — User, group, service principal management and SCIM provisioning
- `references/SAPDatabricks/Networking and security _ SAP Databricks.pdf` — IP allowlisting, egress control, encryption, backup
- `references/SAPDatabricks/Data analysis with notebooks _ SAP Databricks.pdf` — Notebook creation, debugging, scheduling, Git folders, Genie Code
- `references/SAPDatabricks/AI and machine learning _ SAP Databricks.pdf` — Mosaic AI features, model serving, vector search, fine-tuning
- `references/SAPDatabricks/Connect to external data sources _ SAP Databricks.pdf` — Cloud storage connections, Delta Sharing
- `references/SAPDatabricks/Share SAP data into SAP Databricks _ SAP Databricks.pdf` — Mounting SAP data products, semantic metadata
- `references/SAPDatabricks/Publish data from SAP Databricks to SAP BDC _ SAP Databricks.pdf` — Creating and publishing shares back to BDC
- `references/SAPDatabricks/View and query the billing logs _ SAP Databricks.pdf` — Billable usage table schema, pricing queries
- `references/SAPDatabricks/Attribute usage with serverless budget policies _ SAP Databricks.pdf` — Cost attribution via tags and policies
- `references/SAPDatabricks/SAP Databricks API reference _ SAP Databricks.pdf` — REST API endpoints for workspace, account, ML, Unity Catalog
- `references/SAPDatabricks/SAP Databricks documentation _ SAP Databricks.pdf` — Core features, supported regions, architecture
