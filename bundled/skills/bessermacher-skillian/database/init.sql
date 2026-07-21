-- ============================================================================
-- SAP BW Business Database - Table Definitions
-- Database: business_db
-- Tables: fi_reporting, consolidation_mart, bpc_reporting
-- ============================================================================

-- ============================================================================
-- Table: fi_reporting
-- Purpose: Financial Reporting data from SAP BW FI module
-- ============================================================================
CREATE TABLE fi_reporting (
    -- Primary Key Fields (composite key)
    fiscper         VARCHAR(7) NOT NULL,       -- Fiscal year/period (e.g., '2024001')
    fiscvarnt       VARCHAR(2) NOT NULL,       -- Fiscal year variant
    ac_docln        VARCHAR(6) NOT NULL,       -- Line Item (General Ledger View)
    acledger        VARCHAR(2) NOT NULL,       -- Ledger
    ac_docnr        VARCHAR(10) NOT NULL,      -- Document Number (General Ledger View)
    rectype         VARCHAR(1) NOT NULL,       -- Record Type
    version         VARCHAR(10) NOT NULL,      -- Version
    compcode        VARCHAR(4) NOT NULL,       -- Company Code

    -- Characteristics / Dimensions
    custpsg         VARCHAR(10),               -- Customer from PSG
    ref_key         VARCHAR(20),               -- Reference Key
    bill_num        VARCHAR(10),               -- Billing document
    salesorg        VARCHAR(4),                -- Sales Organization
    division        VARCHAR(2),                -- Division
    distchan        VARCHAR(2),                -- Distribution Channel
    merevopa        VARCHAR(10),               -- Profitability Segment (CO-PA)
    asgn_no         VARCHAR(18),               -- Assignment number
    pst_date        DATE,                      -- Posting Date in the Document
    calyear         VARCHAR(4),                -- Calendar Year
    calquarter      VARCHAR(5),                -- Calendar Year/Quarter
    calmonth        VARCHAR(6),                -- Calendar Year/Month
    fiscyear        VARCHAR(4),                -- Fiscal year
    item_num        VARCHAR(3),                -- Line item number within accounting doc
    chrt_acs        VARCHAR(4),                -- Chart of accounts
    gl_acct         VARCHAR(10),               -- G/L Account
    ac_docno        VARCHAR(10),               -- Accounting document number
    doc_date        DATE,                      -- Document Date
    move_tp         VARCHAR(3),                -- Movement Type
    ac_doctp        VARCHAR(2),                -- FI Document type
    prof_ctr        VARCHAR(10),               -- Profit center
    segment         VARCHAR(10),               -- Segment for Segmental Reporting
    pcompany        VARCHAR(6),                -- Partner Company
    pcompcd         VARCHAR(4),                -- Company code of partner
    psegment        VARCHAR(10),               -- Partner Segment
    postxt          VARCHAR(60),               -- Item Text
    dochdtxt        VARCHAR(25),               -- Document Text
    ndcostmr        VARCHAR(10),               -- Non-deductible costs marker
    co_area         VARCHAR(4),                -- Controlling area
    coorder         VARCHAR(12),               -- Order Number
    prodline        VARCHAR(8),                -- Production Line
    funcarea        VARCHAR(16),               -- Functional area
    customer        VARCHAR(10),               -- Customer
    plant           VARCHAR(5),                -- Plant
    sord_itm        VARCHAR(6),                -- Sales document item
    doc_numb        VARCHAR(10),               -- Sales Document
    material        VARCHAR(18),               -- Material
    bwtar           VARCHAR(10),               -- Valuation type
    part_pc         VARCHAR(10),               -- Partner profit center
    costctr         VARCHAR(10),               -- Cost Center
    costelmt        VARCHAR(10),               -- Cost Element
    fi_xblnr        VARCHAR(16),               -- Reference document number
    ref_docn        VARCHAR(16),               -- Reference document number
    ref_clnn        VARCHAR(16),               -- Reference cleaning number
    fidbcrin        VARCHAR(1),                -- Debit/Credit Indicator
    wbs_elmt        VARCHAR(24),               -- WBS Element
    network         VARCHAR(12),               -- Network
    vendor          VARCHAR(10),               -- Vendor
    oi_ebeln        VARCHAR(10),               -- Purchasing document number
    oi_ebelp        VARCHAR(5),                -- Item number of purchasing document
    clrdocno        VARCHAR(10),               -- Clearing Document Number
    clr_date        DATE,                      -- Clearing date

    -- Key Figures
    cs_trn_qty      NUMERIC(17,3),             -- Periodic quantity
    curkey_lc       VARCHAR(5),                -- Currency Key for Local Currency
    cs_trn_lc       NUMERIC(17,2),             -- Period Value in Local Currency
    amnt_dc         NUMERIC(17,2),             -- Amount in document currency
    doc_currcy      VARCHAR(5),                -- Document currency
    quantity        NUMERIC(17,3),             -- Quantity
    unit            VARCHAR(3),                -- Unit of Measure

    -- Metadata
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Primary Key
    PRIMARY KEY (fiscper, fiscvarnt, ac_docln, acledger, ac_docnr, rectype, version, compcode)
);

-- Indexes for fi_reporting
CREATE INDEX idx_fi_compcode ON fi_reporting(compcode);
CREATE INDEX idx_fi_fiscper ON fi_reporting(fiscper);
CREATE INDEX idx_fi_gl_acct ON fi_reporting(gl_acct);
CREATE INDEX idx_fi_prof_ctr ON fi_reporting(prof_ctr);
CREATE INDEX idx_fi_costctr ON fi_reporting(costctr);
CREATE INDEX idx_fi_customer ON fi_reporting(customer);
CREATE INDEX idx_fi_vendor ON fi_reporting(vendor);
CREATE INDEX idx_fi_pst_date ON fi_reporting(pst_date);

-- ============================================================================
-- Table: consolidation_mart
-- Purpose: Consolidation data mart for BPC integration
-- ============================================================================
CREATE TABLE consolidation_mart (
    -- Key Fields
    id              SERIAL PRIMARY KEY,
    pcompcd         VARCHAR(4),                -- Company code of partner
    version         VARCHAR(10) NOT NULL,      -- Version
    fiscper         VARCHAR(7) NOT NULL,       -- Fiscal year/period
    fiscvarnt       VARCHAR(2) NOT NULL,       -- Fiscal year variant
    compcode        VARCHAR(4) NOT NULL,       -- Company Code

    -- Characteristics
    pcompany        VARCHAR(6),                -- Partner Company
    grpacct         VARCHAR(10),               -- Group Account
    pc_area         VARCHAR(20),               -- PC Area
    ppc_area        VARCHAR(20),               -- Partner PC Area
    chrt_acs        VARCHAR(4),                -- Chart of accounts
    gl_acct         VARCHAR(10),               -- G/L Account
    spec            VARCHAR(10),               -- Specifications
    move_tp         VARCHAR(3),                -- Movement Type
    prof_ctr        VARCHAR(10),               -- Profit center
    segment         VARCHAR(10),               -- Segment for Segmental Reporting
    psegment        VARCHAR(10),               -- Partner Segment
    prodh1          VARCHAR(18),               -- Product hierarchy level 1
    prodh2          VARCHAR(18),               -- Product hierarchy level 2
    co_area         VARCHAR(4),                -- Controlling area
    funcarea        VARCHAR(16),               -- Functional area
    bwtar           VARCHAR(10),               -- Valuation type
    part_pc         VARCHAR(10),               -- Partner profit center
    bpc_src         VARCHAR(2),                -- Source of data for BPC Mart

    -- Key Figures
    cs_ytd_qty      NUMERIC(17,3),             -- Cumulative Quantity
    cs_trn_qty      NUMERIC(17,3),             -- Periodic quantity
    unit            VARCHAR(3),                -- Unit of Measure
    cs_ytd_lc       NUMERIC(17,2),             -- Cumulative (YTD) Value in Local Currency
    cs_trn_lc       NUMERIC(17,2),             -- Period Value in Local Currency
    curkey_lc       VARCHAR(5),                -- Currency Key for Local Currency

    -- Metadata
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Unique constraint for business key (includes product hierarchy for granularity)
    UNIQUE (fiscper, fiscvarnt, compcode, version, gl_acct, prof_ctr, pcompcd, prodh1, spec)
);

-- Indexes for consolidation_mart
CREATE INDEX idx_cons_compcode ON consolidation_mart(compcode);
CREATE INDEX idx_cons_fiscper ON consolidation_mart(fiscper);
CREATE INDEX idx_cons_grpacct ON consolidation_mart(grpacct);
CREATE INDEX idx_cons_prof_ctr ON consolidation_mart(prof_ctr);
CREATE INDEX idx_cons_segment ON consolidation_mart(segment);
CREATE INDEX idx_cons_version ON consolidation_mart(version);

-- ============================================================================
-- Table: bpc_reporting
-- Purpose: Business Planning and Consolidation reporting data
-- ============================================================================
CREATE TABLE bpc_reporting (
    -- Key Fields
    id              SERIAL PRIMARY KEY,
    version         VARCHAR(10) NOT NULL,      -- Version
    scope           VARCHAR(10),               -- Scope
    fiscper         VARCHAR(7) NOT NULL,       -- Fiscal year/period
    fiscvarnt       VARCHAR(2) NOT NULL,       -- Fiscal year variant
    compcode        VARCHAR(4) NOT NULL,       -- Company Code

    -- Characteristics
    pc_area         VARCHAR(20),               -- PC Area
    ppc_area        VARCHAR(20),               -- Partner PC Area
    pcompcd         VARCHAR(4),                -- Company code of partner
    grpacct         VARCHAR(10),               -- Group Account
    funcarea        VARCHAR(16),               -- Functional area
    spec            VARCHAR(10),               -- Specifications
    dsource         VARCHAR(30),               -- Data Source

    -- Key Figures
    cs_trn_lc       NUMERIC(17,2),             -- Period Value in Local Currency
    cs_trn_gc       NUMERIC(17,2),             -- Period Value in Group Currency

    -- Metadata
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Unique constraint for business key
    UNIQUE (fiscper, fiscvarnt, compcode, version, grpacct, funcarea)
);

-- Indexes for bpc_reporting
CREATE INDEX idx_bpc_compcode ON bpc_reporting(compcode);
CREATE INDEX idx_bpc_fiscper ON bpc_reporting(fiscper);
CREATE INDEX idx_bpc_grpacct ON bpc_reporting(grpacct);
CREATE INDEX idx_bpc_version ON bpc_reporting(version);
CREATE INDEX idx_bpc_scope ON bpc_reporting(scope);
CREATE INDEX idx_bpc_dsource ON bpc_reporting(dsource);

-- ============================================================================
-- Comments on tables
-- ============================================================================
COMMENT ON TABLE fi_reporting IS 'SAP BW Financial Reporting - Contains FI transactional data with full GL detail';
COMMENT ON TABLE consolidation_mart IS 'SAP BW Consolidation Mart - Aggregated data for BPC consolidation processes';
COMMENT ON TABLE bpc_reporting IS 'SAP BPC Reporting - Business Planning and Consolidation reporting layer';
