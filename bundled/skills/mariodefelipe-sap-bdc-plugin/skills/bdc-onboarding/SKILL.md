---
name: bdc-onboarding
description: Use when the user is setting up SAP BDC for the first time, provisioning the tenant, onboarding admins/users, asking about BDC availability/regions/SLAs, or needs a getting-started walkthrough. Trigger phrases include "set up BDC", "onboard BDC", "BDC tenant", "BDC availability", "BDC regions", "BDC getting started", "first time BDC", "provision BDC".
---

# SAP Business Data Cloud Onboarding Guide

## Prerequisites & Entitlements

Before provisioning SAP BDC, verify you have:
- **S-User ID**: Required to access SAP for Me provisioning portal
- **Commercial entitlement** to SAP Business Data Cloud product package
- **Contact person designation**: Your sales account executive sends initial invitation email with 7-day validity
- **Multi-factor authentication (MFA)**: Required for system owner to create bundled identity tenants
- **Cloud Foundry environment**: Required for BDC tenant deployment and SAP Cloud Identity Services integration

## Phase 1: Tenant Provisioning

### Access SAP for Me
1. Navigate to SAP for Me (https://me.sap.com)
2. Sign in with your S-User ID credentials
3. Go to **Portfolio & Products**
4. Locate **SAP Business Data Cloud** in My Product Packages
5. Access the **Provisioning and Integration Dashboard**

### The Provisioning Dashboard
The dashboard displays:
- **Overview tab**: Current solutions, quota distribution, auto-provisioned SAP Business Warehouse Private Cloud Edition
- **Applications tab**: Where you provision solution components (SAP Datasphere, SAP Databricks, SAP Analytics Cloud)
- **Solutions tab**: Your existing provisioned solutions with status
- **Resources tab**: Resource hierarchies organized into resource groups and folders
- **Customer Landscape tab**: Formation configurations for system integration

### Allocate Capacity Units
- Total capacity units assigned per contract are shown in the Quota Distribution card
- SAP Warehouse Private Cloud Edition receives its contractual quota automatically
- Allocate remaining units to other solutions (SAP Datasphere, Databricks, etc.) as needed during provisioning
- Note: Each solution component = 1 solution + 1 tenant within a single resource group

## Phase 2: Identity Setup (SAP Cloud Identity Services)

### Prerequisites for Bundled Identity
- SAP BDC tenant must be Cloud Foundry-based
- Not available for private cloud (AliCloud) or sovereign cloud (NS2)
- System owner must have MFA enabled
- System owner email must match an S-User ID (create one if needed)

### Provision SAP Cloud Identity Services Tenant
1. In **Identity Provider Administration Tool** (identity.sap.com)
2. On your BDC tenant card, select **+ Add SAP Cloud Identity Services**
3. Choose:
   - **Provision New SCI Tenant**: Auto-matches BDC tenant type (Test, Prod, etc.)
   - **Use Existing SCI Tenant**: Link to already-provisioned tenant
4. For new tenant: Enter administrator first/last name and email (auto-populated from your account)
5. Confirm and start provisioning (takes up to 1 hour)
6. Monitor progress bar; can close and check status later on tenant card

### Configure Authentication
After SCI provisioning completes:
1. Select **Configure Authentication**
2. Choose **User Attribute mapping**:
   - **USER ID**: Map IdP Subject Name Identifier to BDC User ID
   - **Email**: Map to BDC email address
   - **Custom Attribute**: Map to custom field (requires manual SAML User Mapping column updates for existing users)
3. **(Optional) Enable Dynamic User Creation**: New users auto-created with default role upon first login
4. Validate login in test browser (private/guest mode) using provided URL
5. Confirm and finish configuration

**Note**: Subject Name Identifier is case-sensitive; must match exactly (user@company.com ≠ User@company.com)

### Optional: Corporate IdP Federation
Configure SAP Cloud Identity Services to forward SAML authentication to your corporate IdP for centralized identity management.

## Phase 3: Initial Login & Account Activation

- **Owner role** receives Welcome email with activation links (valid 7 days)
- Click activation link to set password; automatically logged in after
- Activation link opens via SAP for Me → BDC Resources tab → main tenant URL
- **If activation expires**: Use "Forgot password?" on login page with the email address from Welcome email
- **If no Welcome email**: Check Spam/Junk folders or contact your account executive

## Phase 4: User Management & Roles

### Core BDC Roles

| Role | Permissions |
|------|-----------|
| **System Owner** | Provision/configure tenant, create identity services, manage MFA |
| **BD Administrator** | Create/manage users, install intelligent applications, activate data packages, manage roles & privileges |
| **DW Administrator** | Manage SAP Datasphere spaces, copy preparation/application spaces, add Modeler users to scoped roles |
| **DW Modeler** | Model data in SAP Datasphere, install data products, adjust view sources |
| **Consumer** | Read access to published analytics and data in SAP Analytics Cloud stories |
| **Standard Role** | Default role assigned to dynamically-created users; auto-created via SAML |

### Create Users
Users with **BD Administrator** role can create accounts in:
- **Security** → **Users** menu
- Assign roles and set user attributes (User ID, Email, Custom Mapping for SAML)
- For SAML-mapped users, ensure **SAML User Mapping** column matches your IdP Subject Name Identifier

### Create Custom Roles
BD Administrators can create custom roles with specific privileges via:
- **Security** → **Users and Roles** → **Create Roles**
- Define granular permissions for intelligent applications and data products

## Phase 5: Install Intelligent Applications

### Prerequisites
- Intelligent application entitlement must be active in your global account
- At least one SAP source system tenant (S/4HANA Cloud, BW/4HANA, etc.) exists in a BDC formation
- **SAP Note 3607594**: Review before installing or updating intelligent applications

### Install Process
1. Open SAP Business Data Cloud cockpit
2. Navigate to **Intelligent Applications and Data Packages** → **Available** tab
3. Select desired application; review documentation and data products
4. Click **Install**; Install Options dialog opens
5. **Source System**: Select SAP system providing business data (connection test runs)
6. **System Alias**: Auto-assigned to distinguish multi-source installations
7. **Business Name** (optional): Custom name appended to Datasphere spaces (up to 200 characters)
8. **Install Location**: Select formation containing source system
9. Click **Install**

### Installation Details
- Status changes to **Installation in progress**
- Creates 3 protected SAP Datasphere spaces (import connections, replication flows, views, analytic models)
- Starts Initial & Delta load replication flows to keep data fresh
- Creates protected SAP Analytics Cloud workspace with stories
- Completion indicated by **Installed** status

### Post-Installation Admin Steps (Datasphere)
1. **Add Modeler users** to preparation space scoped role
2. **Monitor replication flows** for data freshness
3. **Configure row-level security** in preparation space permissions table (max 5,000 permissions per user)
4. **Run delivered task chains** as scheduled
5. **Add Consumer users** to application space scoped role for story/dashboard access

### Post-Installation Admin Steps (Analytics Cloud)
- Grant story folder access to same Consumer users
- Configure appropriate workspace permissions

**Warning**: Install applications sequentially, not in parallel (parallel installation consumes more resources and increases timeout risk).

## Phase 6: Activate Data Packages

### Prerequisites
- **SAP Note 3607594**: Check before activation
- Authorization from BD Administrators
- SAP Datasphere space entitlement for modeling

### Activation Steps
1. Open SAP Business Data Cloud cockpit
2. Navigate to **Intelligent Applications and Data Packages** → **Packages** tab
3. Select package; click **Activate**
4. Status moves to **Active**; data products now available in Catalog for consumption

### Post-Activation
- **Catalog admins**: Share data products to consumer spaces
- **Datasphere admins**: Authorize spaces to install data products
- **Datasphere users**: Install activated products into their modeling spaces

### Optional: Data Product Generator
To replicate SAP BW data into BDC:
1. Configure **Data Product Generator** in source system
2. Create **data subscriptions** to receive incremental updates
3. Monitor refresh status in Datasphere

## Phase 7: Manage Lifecycle (Updates, Deactivation, Uninstall)

### Update Intelligent Applications & Packages
- **SAP Note 3607594**: Check for update prerequisites before each upgrade
- Status shows **Update Available** when new version released
- Updates include fixes, improvements, or new KPIs
- Click **Update** to install latest version

### Deactivate Data Packages
- Used when package no longer needed or entitlement expires
- Before deactivating, check with SAP Admin whether entitlement renewal is planned
- BD Administrators perform deactivation via **Packages** tab

### Uninstall Intelligent Applications
- Manual uninstall available when application no longer needed
- Used when entitlement has expired/terminated
- Before uninstalling, consult with SAP Administrator
- Removes all SAP Datasphere spaces and SAP Analytics Cloud content

## Service Availability & Regions

### Supported Regions (Controlled Release Rollout)
Current deployments across AWS, Azure, GCP hyperscalers:
- **AWS**: EU (Frankfurt EU10), Australia (AP10), Singapore (AP11), Tokyo (JP10), US East/Virginia (US10), Canada Montreal (CA10), Korea (AP12), Brazil (BR10), US West (US20), US East (US21), Brazil (BR20), Canada (CA20), Switzerland (CH20), Australia (AP20), Singapore (AP21)
- **Azure**: Europe Amsterdam (EU20), Switzerland (CH20)
- **GCP**: EU Frankfurt (EU30), India Mumbai (IN30), Saudi Arabia Dammam (SA30/SA31), US Iowa (US30)

Note: Solution component availability varies by region due to compliance/buildout timelines. Contact Account Executive for regional roadmap.

### Browser Support
- **Google Chrome**: Latest version (continuous updates)
- **Microsoft Edge**: Chromium-based, latest version
- Exceptional instances may limit support; see browser documentation for full requirements

### Compliance & Security
- **BDC itself** is not certified; component certifications apply to SAP Datasphere, SAP Analytics Cloud, BTP
- **Data protection**: Follows SAP global guidelines; see Personal Data Processing for SAP Cloud Services
- **SLA**: Refer to Service Level Agreement for SAP Cloud Services (covers uptime, credits, update windows)
- **Maintenance windows**: Check SAP Help Portal Maintenance Windows for SAP Cloud Services (search for your service)

## Common First-Day Pitfalls

1. **Activation link expiration**: Set password within 7 days of Welcome email
2. **SAML identity mismatch**: Subject Name Identifier must match BDC user attribute case-sensitively
3. **Missing entitlements**: Verify intelligent application & data package entitlements before installation
4. **Parallel installations**: Install applications sequentially to avoid timeouts
5. **Permissions not configured**: Row-level security requires explicit permission table setup in Datasphere
6. **User attribute mapping mismatch**: Dynamic user creation requires matching IdP attributes with BDC User ID/Email
7. **MFA not enabled**: System owner requires MFA for bundled identity services setup
8. **Region limitations**: Not all features available in all regions; check availability table for limitations

## Support & References

- **SAP Note 3607594**: Prerequisites for installing/updating intelligent applications
- **SAP Note 3568017**: Providing support user access for troubleshooting
- **SAP Note 3619907**: Bundled SAP Cloud Identity Services controlled release status
- **Contact**: Sales Account Executive or Customer Interaction Center (CIC) for provisioning assistance
- **Help Portal**: https://help.sap.com/docs/SAP_BUSINESS_DATA_CLOUD

---

## References
- `references/onboarding.pdf` — Complete SAP BDC onboarding guide (35 pages)
- `references/availability.pdf` — Regions, SLAs, compliance, and browser support (4 pages)
