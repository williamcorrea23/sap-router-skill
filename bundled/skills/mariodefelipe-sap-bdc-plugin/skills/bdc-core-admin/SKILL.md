---
name: bdc-core-admin
description: Use when the user is administering SAP BDC — managing users/roles, provisioning spaces/tenants, monitoring system health, configuring auth (IdP/SCIM), managing capacity, or troubleshooting admin-level issues. Trigger phrases include "BDC admin", "BDC user management", "BDC roles", "BDC provisioning", "BDC tenant admin", "BDC monitoring", "BDC capacity", "BDC identity", "BDC SCIM".
---

# SAP BDC Core Administration

SAP Business Data Cloud (BDC) is a fully managed SaaS solution for governing enterprise data across SAP and third-party sources. Administrators with the **BD Administrator** role provision systems, configure identity, manage users and roles, monitor system health, and manage capacity across the BDC product suite.

## User and Role Management

Administrators with the **BD Administrator** role create and manage BDC users, assign roles and privileges, and control access through the Users and Roles pages in the BDC cockpit.

### Creating Users

Individual users can be created via the Users page, imported from CSV files, or mapped automatically via SAML attributes.

#### Use the Users Page

Navigate to **Security > Users** and select **Create User**:

- **User ID**: Required, unique identifier. Alphanumeric (A-Z, 0-9) and underscores only, max 20 characters. Cannot be modified after creation.
- **Email Address**: Receives welcome email with logon details.
- **User Name**: First Name, Last Name (mandatory), Display Name. Display Name appears on user-facing screens.
- **Manager**: Optional field to set reporting relationship.
- **Role Assignment**: Select one or more roles (standard or custom). If none selected, default role applies.
- **Review and Save**: Confirm details before creating account.

Results: Welcome email sent to user with account activation URL and password setup instructions.

#### Import Users from CSV File

Create bulk users by importing CSV data with required columns: **UserID**, **LastName**, **Email**. Recommended to include **FirstName** and **DisplayName**.

Role assignment: Include a **Roles** column with role IDs (from Standard Roles Delivered with SAP Business Data Cloud reference). If omitted, default role assigned.

Navigate to **Security > Users > Import Users from File**:

1. Select CSV source file.
2. Define mapping for Header, Line Separator, Delimiter, Text Qualifier.
3. Map CSV fields to BDC user attributes: User ID, First Name, Last Name, Display Name, Email, Manager, Roles, Mobile, Phone, Office Location, Function Area, Job Title.
4. Click Import.

Limitations: First Name, Last Name, and Display Name are linked to the IdP and cannot be modified via import. Users must edit their own profile to change these values.

### Modifying Users

Update existing user email addresses, roles, SAML attributes, or account status via **Security > Users > Edit User** or batch update with CSV re-import.

**Update Email Address**: Select user from Users page, click Edit User, modify email, proceed to next step, review, and save.

**Batch Modification via CSV**: Export existing users to CSV, edit the file (keeping UserID unchanged), re-import with updated values. Do not modify the UserID column to ensure matching to existing users.

**Edit SAML Mappings**: Map SAML user attributes to BDC profile fields:
- First Name
- Last Name
- Display Name
- E-Mail
- Functional Area

Navigate to **Security > Users > Map SAML User Properties**, select SAML Attribute, assign Target Property, and save. User profiles update with latest IdP information on next logon.

## Role and Privilege Management

### Standard Roles

Predefined roles in BDC include **BD Administrator**, **BD Viewer**, **DW Consumer**, **Data Steward**, and **Catalog Viewer**. Each role includes specific privileges and permissions appropriate to job function.

- **BD Administrator**: Full administrative control. Provision systems, manage users/roles, install intelligent applications, activate data packages, configure identity, monitor system landscape.
- **BD Viewer**: Monitor systems and navigate to formations. View intelligent applications.
- **DW Consumer**: Consume data products prepared by SAP Datasphere in Analytics Cloud.
- **Data Steward**: Set up and implement data governance using the catalog, connect systems, create glossaries, manage KPIs and tags.
- **Catalog Viewer**: Search and discover data and analytics content in catalog for consumption.

### Creating and Managing Custom Roles

Tenant administrators create custom roles by selecting individual privileges and permissions for specific business needs, then assign to users. Navigate to **Security > Roles** to create or modify roles.

### Privileges and Permissions

**Global Privileges** control access to major areas:
- **System Information**: View system configuration, session timeout settings, notifications, audit logs.
- **User Management**: Create, read, update, delete users. Manage user roles and attributes.
- **Role Management**: Create, read, update, delete custom roles and assign privileges.
- **Catalog Access**: Browse assets, view details, publish/unpublish content.
- **Glossary Management**: Create and maintain glossary terms.
- **KPI Management**: Create and manage KPIs.
- **Content Network**: Import SAP and partner business content.
- **Intelligent Applications**: Install, update, manage applications and data packages.

**Permissions** for each privilege:
- **View**: Open and view items and content.
- **Maintain**: Edit and update existing items.
- **Delete**: Remove items from system.
- **Create**: Generate new items.
- **Publish**: Expose items for consumption.

## Identity Configuration and Single Sign-On

Administrators configure how users authenticate to BDC via Identity Provider (IdP) integration or bundled SAP Cloud Identity Services.

### Setting Up Custom SAML Identity Provider

To establish trust with a custom SAML IdP and enable SSO:

1. **Exchange Metadata**: Exchange SAML metadata between BDC and custom IdP to establish trust relationship.
2. **Upload IdP Metadata**: In **Security > Single Sign-On**, upload IdP metadata (SAML XML) to configure authentication.
3. **Map SAML Attributes**: Configure attribute mapping from IdP assertions to BDC user profiles (First Name, Last Name, Display Name, Email, Functional Area).
4. **Open Support Case**: For first-time SAML configuration or IdP switch, open case with SAP support providing BDC tenant URL and S-User details.

User profiles update automatically with latest IdP information on logon.

### Provisioning Bundled SAP Cloud Identity Services

Alternatively, provision a bundled SAP Cloud Identity Services tenant for centralized SSO management across BDC and other SAP products:

1. Tenant system owner initiates provisioning in **SAP for Me > Provisioning and Integration Dashboard**.
2. Provide Identity Services tenant administrator name, email, and IAS tenant name.
3. System owner must have multi-factor authentication (MFA) enabled on S-User account.

Benefits: Unified identity and access management, reduced operational overhead for multiple IdPs.

### Switching Identity Providers

To switch from one SAML IdP to another:

1. Repeat metadata exchange and upload steps with new IdP.
2. Open support case with SAP (required each IdP switch).
3. Run Verify Account step using provided links to migrate user accounts safely.

Previous IdP configurations are retained to allow parallel authentication during transition.

## System Provisioning and Capacity Management

### Provisioning BDC Applications in SAP for Me

Users with S-User ID access the **Provisioning and Integration Dashboard** in **SAP for Me** to provision BDC applications:

- **SAP Datasphere**: Unified data governance and analytics warehouse.
- **SAP Analytics Cloud**: Analytics and business intelligence.
- **SAP Databricks**: AI/ML analytics platform.
- **SAP Business Data Cloud Connect**: Data integration and sharing.

**Common Provisioning Parameters**:
- **Tenant Host Name**: Unique identifier for tenant URL (e.g., `https://<Tenant Host Name>.eu10.sapdatasphere.cloud`).
- **Region**: Geographic data center location.
- **Size**: Capacity allocation (see Capacity Unit Estimator).
- **Owner**: Administrator assigned to manage tenant.

Navigate to **Applications** tab, select application tile, choose **Start Provisioning**, complete parameters, and submit.

### Capacity Unit Allocation

SAP BDC product suite consumes capacity units (CUs) based on provisioned applications and configurations. Use the **SAP Business Data Cloud Capacity Unit Estimator** tool to calculate CU requirements per service.

Monitor CU usage in **Provisioning and Integration Dashboard > Quota Distribution** card to track enabled units vs. consumed capacity.

### Updating Provisioned Tenants

Edit provisioned application configurations (e.g., size, region) via **Provisioning and Integration Dashboard > Applications** tab. Select application, click **Edit**, update parameters, and save. Changes apply at next maintenance window.

**Rewiring SAP Datasphere or Analytics Cloud**: Systems can be rewired to different BDC formations. User with BTP Cockpit access logs in, manages service instances, and updates formation associations. Update capacity unit allocations after rewiring.

## System Landscape Monitoring and Connectivity

### Monitoring System Connectivity

Users with **BD Administrator** and **BD Viewer** roles monitor systems in **Integration with SAP Business Data Cloud** formations and navigate directly to them.

Navigate to **System Landscape Monitoring** to:

- View connectivity status of integrated systems (SAP S/4HANA, SAP Analytics Cloud, SAP Databricks, SAP Customer Data Platform, SuccessFactors, etc.).
- Identify connection issues between BDC and source systems.
- Monitor replication and data flow status.
- Access system details and configuration parameters.

### System Formation Landscape

BDC landscape consists of multiple formations (logical groupings of integrated systems):

- **Formation Type**: Integration with SAP Business Data Cloud
- **Customer Landscape Tab**: Displays all formations and integrated systems
- **System Details**: Access tenant configuration, system IDs, namespaces, connection status

## System Configuration and Administration

### Session Management

Administrators configure session timeout behavior via **System > Administration > System Configuration**:

- **Session Timeout**: Time (in seconds) before user session expires due to inactivity. Default: 3600 seconds (1 hour). Minimum configurable value available.

### Notification Configuration

Administrators manage notifications for system events and connection issues via **System > Administration > Notifications**:

**System Event Notifications**: 
- In case of service interruption, send notification emails to selected users (system owner and other recipients).
- Enable/disable in Notifications section with email recipient list.

**Connection and Performance Notifications**:
- Notify users viewing stories about potential network connection issues or performance problems.
- Enable toggle in Connections Notifications section.
- When enabled, notification displays in top-right corner of application for all users on tenant.

### SMTP Server Configuration

Configure outbound email delivery for notifications by specifying SMTP server details in **System > Administration > Notifications**.

### User Profile Settings

Individual users can access personal settings via user icon in shell bar > **Settings** to manage:
- Email address and contact information
- Notification preferences
- Welcome message and page tips visibility
- Locale and language settings

### Number Format and Display Settings

Configure system-wide display settings via **System > Administration > System Configuration**:
- **Number Scale Format**: System default, short notation (k, m, bn), or long (Thousand, Million, Billion)
- **Currency Position**: Display convention for currency symbols

## Activity Tracking and Auditing

### Tracking User Activities

Users with audit privileges view activities via **System > Administration > Activities**:

Activities include:
- Intelligent application and data package installations, updates, uninstallations
- Catalog administration actions (asset publishing, glossary creation)
- Role changes and user assignments

Each activity logged with correlation ID for troubleshooting and audit trails.

**Export Activity Data**: Download activity records as CSV (max 75,000 rows per file) within specified date range and filters.

### Identity Provider Settings and Logging

Record and monitor IdP configuration changes, trust relationships, metadata uploads, and SAML authentication failures for compliance and troubleshooting.

## Intelligent Applications and Data Package Management

### Installing Intelligent Applications

Users with **BD Administrator** role install pre-built intelligent applications from SAP or partners into BDC formations.

Navigate to **Intelligent Applications and Data Packages**:

1. Review available applications and prerequisites (Datasphere space availability, Analytics Cloud folder access).
2. Select application and choose **Install**.
3. Specify target formation, Datasphere space, and Analytics Cloud folder.
4. Monitor installation status (Queued, Waiting, Installing, Installed, Failed).
5. Grant access permissions to target Analytics Cloud stories/folders for intended user groups.

Multiple applications can share same Datasphere and Analytics Cloud tenants. Installations are tracked with date/time of creation and last modification.

### Managing Data Products and Packages

**Data Packages**: Collections of related data products for modeling projects.

**Activating Data Packages**:

Navigate to **Intelligent Applications and Data Packages > Data Packages**:

1. Select package and choose **Activate**.
2. Specify target Datasphere space for deployment.
3. Monitor activation status (same as applications above).
4. View provisioning and lifecycle status of individual data products within package.

**Deactivating Packages**: Remove package from Datasphere and Analytics Cloud, reverting environment to pre-activation state.

**Cleaning Up Failed Installations**: If installation/activation/deactivation fails, use cleanup function to reset environment and remove partially installed artifacts.

**Retrying Failed Operations**: Rerun failed installation, activation, or deactivation after resolving root cause (connection issues, space availability, permissions).

## Security Best Practices and Compliance

### Identity and Access Control

- **Principle of Least Privilege**: Assign minimum privileges needed for job function. Avoid overprovisioning users with elevated roles.
- **SAML Attribute Mapping**: Map only user attributes and roles actually used in BDC to minimize attack surface.
- **MFA Enforcement**: Require multi-factor authentication for system owners and administrators.
- **Regular Access Reviews**: Periodically audit user roles, privileges, and active accounts to identify orphaned or excessive permissions.

### Intelligent Application Access Control

- **Grant Target Permissions**: Explicitly grant user access to Analytics Cloud folders and stories delivered by intelligent applications.
- **Business User Identification**: Document which business users should access specific intelligent applications based on job role.

### Audit and Monitoring

- **Audit Logging**: Enable audit policies and set retention periods (1-365 days) for compliance.
- **Activity Tracking**: Review audit logs regularly for unauthorized access attempts, privilege escalation, data package modifications.
- **Notification Management**: Configure system event and performance notifications for timely incident detection.

### Data Privacy

External partners, systems, and data sources integrated with BDC may reside in jurisdictions with different data privacy regulations. BDC administrators are responsible for:

- Verifying data residency requirements before provisioning
- Ensuring GDPR/CCPA compliance for customer data
- Documenting data lineage and compliance obligations
- Controlling PII exposure through role-based access

## Common Administrative Tasks

### Exporting and Backing Up User Lists

Export existing users to CSV via **Security > Users > Export Users** for backup or migration:

1. Navigate to Users page
2. Click Export Users
3. CSV includes UserID, FirstName, LastName, DisplayName, Email, Manager, Roles, and other user attributes
4. Store CSV securely; contains user identification data

### Bulk User Onboarding Workflow

1. Prepare CSV file with new users (UserID, Email, FirstName, LastName, DisplayName, Roles)
2. Navigate to **Security > Users > Import Users from File**
3. Upload CSV and define field mappings
4. Import users; welcome emails sent automatically
5. Users activate accounts via email link and set initial password
6. Assign additional roles or permissions as needed post-creation

### Troubleshooting Installation Failures

If intelligent application or data package installation fails:

1. Check **System Landscape Monitoring** for connectivity issues with source systems
2. Verify Datasphere space exists and has available storage/capacity
3. Confirm user has granted Analytics Cloud folder access
4. Review installation status details for error message
5. Resolve root cause (connection, capacity, permissions)
6. Use **Retry** to rerun failed installation
7. If retry fails, use **Clean up** to reset environment state

## Client and System Requirements

### Browser and Network

- **Browsers**: Google Chrome (latest) or Microsoft Edge Chromium-based (latest)
- **Network Bandwidth**: Minimum 500-800 kbit/s per user
- **Screen Resolution**: XGA 1024x768 or higher (widescreen 1366x766+)
- **HTTP/1.1, JavaScript, Cookies**: All required to be enabled
- **Browser Cache**: Minimum 250 MB recommended to cache static content

### Supported Languages

BDC UI available in 50+ languages: English (en-US, en-GB), German, French, Spanish, Chinese (Simplified and Traditional), Japanese, Korean, and 40+ others.

## Support-workflow helpers

### Generating a browser HAR file for a Databricks UI issue (SAP Note 3600390)

When SAP support asks for a network trace of a BDC Databricks UI problem:

1. Open the Databricks workspace in Chrome/Edge.
2. Open DevTools (`F12` or `Cmd+Opt+I`) → Network tab.
3. Check "Preserve log" and "Disable cache".
4. Reproduce the issue.
5. Right-click in the Network panel → "Save all as HAR with content".
6. Attach the `.har` to the support case. Detailed browser-specific steps are in SAP Note 2969368 (referenced by 3600390).

## References

- `references/administering.pdf` — full BDC administration guide (140 pages)
- SAP Note 3500131 — ABAP Data Integration for BDC
- SAP Note 3499606 — User role file for S/4HANA integration
- SAP Note 2441124 — User and role administration
- SAP Note 3600390 — Generate browser HAR files (Databricks in BDC)
- SAP Note 2969368 — Browser-specific HAR recording procedure
- SAP Business Data Cloud Capacity Unit Estimator — calculate CU requirements
- SAP Cloud Identity Services documentation — bundled IdP setup
