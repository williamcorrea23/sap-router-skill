-- ============================================================================
-- SAP BW Business Database - Mock Data Seed
-- Realistic data for SAP BW FI (Financial Accounting) and BPC
-- (Business Planning and Consolidation) scenarios
-- ============================================================================

-- ============================================================================
-- fi_reporting - Financial transactions
-- Represents typical FI postings: vendor invoices, customer invoices,
-- GL postings, asset transactions, intercompany transactions
-- ============================================================================

-- Company 1000 (HQ - Germany) - Revenue and COGS transactions
INSERT INTO fi_reporting (
    fiscper, fiscvarnt, ac_docln, acledger, ac_docnr, rectype, version, compcode,
    custpsg, salesorg, division, distchan, pst_date, calyear, calmonth, fiscyear,
    chrt_acs, gl_acct, ac_docno, doc_date, ac_doctp, prof_ctr, segment,
    funcarea, customer, material, fidbcrin, curkey_lc, cs_trn_lc, amnt_dc,
    doc_currcy, quantity, unit, postxt
) VALUES
-- Customer Invoice - Product Sales
('2024001', 'K4', '001', '0L', '0100000001', '0', 'ACTUAL', '1000',
 'CUST001', '1000', '01', '10', '2024-01-15', '2024', '202401', '2024',
 'CAGR', '4000000', '0100000001', '2024-01-15', 'DR', 'PC1001', 'SEG01',
 'SALES', 'CUST001', 'MAT001', 'S', 'EUR', 125000.00, 125000.00,
 'EUR', 500.000, 'PC', 'Product A Sales Q1'),

('2024001', 'K4', '002', '0L', '0100000001', '0', 'ACTUAL', '1000',
 'CUST001', '1000', '01', '10', '2024-01-15', '2024', '202401', '2024',
 'CAGR', '1400000', '0100000001', '2024-01-15', 'DR', 'PC1001', 'SEG01',
 'SALES', 'CUST001', 'MAT001', 'H', 'EUR', -125000.00, -125000.00,
 'EUR', -500.000, 'PC', 'AR - Product A Sales'),

-- COGS Entry
('2024001', 'K4', '001', '0L', '0100000002', '0', 'ACTUAL', '1000',
 NULL, '1000', '01', '10', '2024-01-15', '2024', '202401', '2024',
 'CAGR', '5000000', '0100000002', '2024-01-15', 'SA', 'PC1001', 'SEG01',
 'COGS', NULL, 'MAT001', 'S', 'EUR', 75000.00, 75000.00,
 'EUR', 500.000, 'PC', 'COGS Product A'),

('2024001', 'K4', '002', '0L', '0100000002', '0', 'ACTUAL', '1000',
 NULL, '1000', '01', '10', '2024-01-15', '2024', '202401', '2024',
 'CAGR', '1300000', '0100000002', '2024-01-15', 'SA', 'PC1001', 'SEG01',
 'COGS', NULL, 'MAT001', 'H', 'EUR', -75000.00, -75000.00,
 'EUR', -500.000, 'PC', 'Inventory reduction'),

-- Operating Expenses - Personnel
('2024001', 'K4', '001', '0L', '0100000003', '0', 'ACTUAL', '1000',
 NULL, NULL, NULL, NULL, '2024-01-31', '2024', '202401', '2024',
 'CAGR', '6200000', '0100000003', '2024-01-31', 'SA', 'PC1001', 'SEG01',
 'ADMIN', NULL, NULL, 'S', 'EUR', 45000.00, 45000.00,
 'EUR', NULL, NULL, 'Salaries January'),

('2024001', 'K4', '002', '0L', '0100000003', '0', 'ACTUAL', '1000',
 NULL, NULL, NULL, NULL, '2024-01-31', '2024', '202401', '2024',
 'CAGR', '2100000', '0100000003', '2024-01-31', 'SA', 'PC1001', 'SEG01',
 'ADMIN', NULL, NULL, 'H', 'EUR', -45000.00, -45000.00,
 'EUR', NULL, NULL, 'Bank - Salaries'),

-- Vendor Invoice - Operating costs
('2024001', 'K4', '001', '0L', '0100000004', '0', 'ACTUAL', '1000',
 NULL, NULL, NULL, NULL, '2024-01-20', '2024', '202401', '2024',
 'CAGR', '6300000', '0100000004', '2024-01-20', 'KR', 'PC1001', 'SEG01',
 'ADMIN', NULL, NULL, 'S', 'EUR', 8500.00, 8500.00,
 'EUR', NULL, NULL, 'Office supplies'),

('2024001', 'K4', '002', '0L', '0100000004', '0', 'ACTUAL', '1000',
 NULL, NULL, NULL, NULL, '2024-01-20', '2024', '202401', '2024',
 'CAGR', '2000000', '0100000004', '2024-01-20', 'KR', 'PC1001', 'SEG01',
 'ADMIN', NULL, NULL, 'H', 'EUR', -8500.00, -8500.00,
 'EUR', NULL, NULL, 'AP - Office supplies'),

-- February transactions
('2024002', 'K4', '001', '0L', '0100000010', '0', 'ACTUAL', '1000',
 'CUST002', '1000', '01', '10', '2024-02-10', '2024', '202402', '2024',
 'CAGR', '4000000', '0100000010', '2024-02-10', 'DR', 'PC1001', 'SEG01',
 'SALES', 'CUST002', 'MAT002', 'S', 'EUR', 180000.00, 180000.00,
 'EUR', 600.000, 'PC', 'Product B Sales Q1'),

('2024002', 'K4', '002', '0L', '0100000010', '0', 'ACTUAL', '1000',
 'CUST002', '1000', '01', '10', '2024-02-10', '2024', '202402', '2024',
 'CAGR', '1400000', '0100000010', '2024-02-10', 'DR', 'PC1001', 'SEG01',
 'SALES', 'CUST002', 'MAT002', 'H', 'EUR', -180000.00, -180000.00,
 'EUR', -600.000, 'PC', 'AR - Product B'),

-- Company 2000 (US Subsidiary) - USD transactions
('2024001', 'K4', '001', '0L', '0200000001', '0', 'ACTUAL', '2000',
 'CUST100', '2000', '01', '10', '2024-01-18', '2024', '202401', '2024',
 'CAGR', '4000000', '0200000001', '2024-01-18', 'DR', 'PC2001', 'SEG02',
 'SALES', 'CUST100', 'MAT001', 'S', 'USD', 95000.00, 95000.00,
 'USD', 350.000, 'PC', 'US Sales - Product A'),

('2024001', 'K4', '002', '0L', '0200000001', '0', 'ACTUAL', '2000',
 'CUST100', '2000', '01', '10', '2024-01-18', '2024', '202401', '2024',
 'CAGR', '1400000', '0200000001', '2024-01-18', 'DR', 'PC2001', 'SEG02',
 'SALES', 'CUST100', 'MAT001', 'H', 'USD', -95000.00, -95000.00,
 'USD', -350.000, 'PC', 'AR - US Sales'),

-- Intercompany transaction (1000 sells to 2000)
('2024001', 'K4', '001', '0L', '0100000005', '0', 'ACTUAL', '1000',
 NULL, '1000', '01', '20', '2024-01-25', '2024', '202401', '2024',
 'CAGR', '4100000', '0100000005', '2024-01-25', 'DR', 'PC1001', 'SEG01',
 'SALES', NULL, 'MAT001', 'S', 'EUR', 50000.00, 50000.00,
 'EUR', 200.000, 'PC', 'IC Sales to US Sub'),

('2024001', 'K4', '002', '0L', '0100000005', '0', 'ACTUAL', '1000',
 NULL, '1000', '01', '20', '2024-01-25', '2024', '202401', '2024',
 'CAGR', '1410000', '0100000005', '2024-01-25', 'DR', 'PC1001', 'SEG01',
 'SALES', NULL, 'MAT001', 'H', 'EUR', -50000.00, -50000.00,
 'EUR', -200.000, 'PC', 'IC AR - US Sub'),

-- Company 3000 (UK Subsidiary) - GBP transactions
('2024001', 'K4', '001', '0L', '0300000001', '0', 'ACTUAL', '3000',
 'CUST200', '3000', '01', '10', '2024-01-22', '2024', '202401', '2024',
 'CAGR', '4000000', '0300000001', '2024-01-22', 'DR', 'PC3001', 'SEG03',
 'SALES', 'CUST200', 'MAT003', 'S', 'GBP', 78000.00, 78000.00,
 'GBP', 280.000, 'PC', 'UK Sales - Product C'),

('2024001', 'K4', '002', '0L', '0300000001', '0', 'ACTUAL', '3000',
 'CUST200', '3000', '01', '10', '2024-01-22', '2024', '202401', '2024',
 'CAGR', '1400000', '0300000001', '2024-01-22', 'DR', 'PC3001', 'SEG03',
 'SALES', 'CUST200', 'MAT003', 'H', 'GBP', -78000.00, -78000.00,
 'GBP', -280.000, 'PC', 'AR - UK Sales'),

-- Cost Center postings
('2024001', 'K4', '001', '0L', '0100000006', '0', 'ACTUAL', '1000',
 NULL, NULL, NULL, NULL, '2024-01-31', '2024', '202401', '2024',
 'CAGR', '6100000', '0100000006', '2024-01-31', 'SA', 'PC1001', 'SEG01',
 'RND', NULL, NULL, 'S', 'EUR', 35000.00, 35000.00,
 'EUR', NULL, NULL, 'R&D Costs January'),

('2024001', 'K4', '002', '0L', '0100000006', '0', 'ACTUAL', '1000',
 NULL, NULL, NULL, NULL, '2024-01-31', '2024', '202401', '2024',
 'CAGR', '2100000', '0100000006', '2024-01-31', 'SA', 'PC1001', 'SEG01',
 'RND', NULL, NULL, 'H', 'EUR', -35000.00, -35000.00,
 'EUR', NULL, NULL, 'Bank - R&D'),

-- Depreciation entries
('2024001', 'K4', '001', '0L', '0100000007', '0', 'ACTUAL', '1000',
 NULL, NULL, NULL, NULL, '2024-01-31', '2024', '202401', '2024',
 'CAGR', '6400000', '0100000007', '2024-01-31', 'AF', 'PC1001', 'SEG01',
 'ADMIN', NULL, NULL, 'S', 'EUR', 12500.00, 12500.00,
 'EUR', NULL, NULL, 'Depreciation Jan'),

('2024001', 'K4', '002', '0L', '0100000007', '0', 'ACTUAL', '1000',
 NULL, NULL, NULL, NULL, '2024-01-31', '2024', '202401', '2024',
 'CAGR', '0900000', '0100000007', '2024-01-31', 'AF', 'PC1001', 'SEG01',
 'ADMIN', NULL, NULL, 'H', 'EUR', -12500.00, -12500.00,
 'EUR', NULL, NULL, 'Accum Depr Jan'),

-- Q1 Additional entries for variance analysis
('2024003', 'K4', '001', '0L', '0100000020', '0', 'ACTUAL', '1000',
 'CUST001', '1000', '01', '10', '2024-03-15', '2024', '202403', '2024',
 'CAGR', '4000000', '0100000020', '2024-03-15', 'DR', 'PC1001', 'SEG01',
 'SALES', 'CUST001', 'MAT001', 'S', 'EUR', 145000.00, 145000.00,
 'EUR', 580.000, 'PC', 'Product A Sales Mar'),

('2024003', 'K4', '002', '0L', '0100000020', '0', 'ACTUAL', '1000',
 'CUST001', '1000', '01', '10', '2024-03-15', '2024', '202403', '2024',
 'CAGR', '1400000', '0100000020', '2024-03-15', 'DR', 'PC1001', 'SEG01',
 'SALES', 'CUST001', 'MAT001', 'H', 'EUR', -145000.00, -145000.00,
 'EUR', -580.000, 'PC', 'AR - Mar Sales');

-- ============================================================================
-- consolidation_mart - Aggregated data for BPC consolidation
-- Contains intercompany balances, segment data, and elimination entries
-- ============================================================================

INSERT INTO consolidation_mart (
    pcompcd, version, fiscper, fiscvarnt, compcode, pcompany, grpacct,
    pc_area, ppc_area, chrt_acs, gl_acct, spec, move_tp, prof_ctr, segment,
    psegment, prodh1, prodh2, co_area, funcarea, bwtar, part_pc, bpc_src,
    cs_ytd_qty, cs_trn_qty, unit, cs_ytd_lc, cs_trn_lc, curkey_lc
) VALUES
-- Company 1000 Revenue by segment
(NULL, 'ACTUAL', '2024001', 'K4', '1000', NULL, 'G4000000',
 'EMEA', NULL, 'CAGR', '4000000', 'REV', NULL, 'PC1001', 'SEG01',
 NULL, 'PROD_A', 'HARDWARE', '1000', 'SALES', NULL, NULL, 'FI',
 500.000, 500.000, 'PC', 125000.00, 125000.00, 'EUR'),

(NULL, 'ACTUAL', '2024002', 'K4', '1000', NULL, 'G4000000',
 'EMEA', NULL, 'CAGR', '4000000', 'REV', NULL, 'PC1001', 'SEG01',
 NULL, 'PROD_B', 'SOFTWARE', '1000', 'SALES', NULL, NULL, 'FI',
 1100.000, 600.000, 'PC', 305000.00, 180000.00, 'EUR'),

(NULL, 'ACTUAL', '2024003', 'K4', '1000', NULL, 'G4000000',
 'EMEA', NULL, 'CAGR', '4000000', 'REV', NULL, 'PC1001', 'SEG01',
 NULL, 'PROD_A', 'HARDWARE', '1000', 'SALES', NULL, NULL, 'FI',
 1680.000, 580.000, 'PC', 450000.00, 145000.00, 'EUR'),

-- Company 1000 COGS
(NULL, 'ACTUAL', '2024001', 'K4', '1000', NULL, 'G5000000',
 'EMEA', NULL, 'CAGR', '5000000', 'COGS', NULL, 'PC1001', 'SEG01',
 NULL, 'PROD_A', 'HARDWARE', '1000', 'COGS', NULL, NULL, 'FI',
 500.000, 500.000, 'PC', 75000.00, 75000.00, 'EUR'),

-- Company 1000 Operating expenses
(NULL, 'ACTUAL', '2024001', 'K4', '1000', NULL, 'G6200000',
 'EMEA', NULL, 'CAGR', '6200000', 'OPEX', NULL, 'PC1001', 'SEG01',
 NULL, NULL, NULL, '1000', 'ADMIN', NULL, NULL, 'FI',
 NULL, NULL, NULL, 45000.00, 45000.00, 'EUR'),

-- Company 2000 Revenue (US)
(NULL, 'ACTUAL', '2024001', 'K4', '2000', NULL, 'G4000000',
 'AMER', NULL, 'CAGR', '4000000', 'REV', NULL, 'PC2001', 'SEG02',
 NULL, 'PROD_A', 'HARDWARE', '2000', 'SALES', NULL, NULL, 'FI',
 350.000, 350.000, 'PC', 95000.00, 95000.00, 'USD'),

-- Company 3000 Revenue (UK)
(NULL, 'ACTUAL', '2024001', 'K4', '3000', NULL, 'G4000000',
 'EMEA', NULL, 'CAGR', '4000000', 'REV', NULL, 'PC3001', 'SEG03',
 NULL, 'PROD_C', 'SERVICES', '3000', 'SALES', NULL, NULL, 'FI',
 280.000, 280.000, 'PC', 78000.00, 78000.00, 'GBP'),

-- Intercompany entries (for elimination)
('2000', 'ACTUAL', '2024001', 'K4', '1000', '002000', 'G4100000',
 'EMEA', 'AMER', 'CAGR', '4100000', 'IC_REV', NULL, 'PC1001', 'SEG01',
 'SEG02', 'PROD_A', 'HARDWARE', '1000', 'SALES', NULL, 'PC2001', 'FI',
 200.000, 200.000, 'PC', 50000.00, 50000.00, 'EUR'),

('1000', 'ACTUAL', '2024001', 'K4', '2000', '001000', 'G5100000',
 'AMER', 'EMEA', 'CAGR', '5100000', 'IC_COGS', NULL, 'PC2001', 'SEG02',
 'SEG01', 'PROD_A', 'HARDWARE', '2000', 'COGS', NULL, 'PC1001', 'FI',
 200.000, 200.000, 'PC', 50000.00, 50000.00, 'EUR'),

-- IC Elimination entries
('2000', 'ACTUAL', '2024001', 'K4', '1000', '002000', 'G4100000',
 'EMEA', 'AMER', 'CAGR', '4100000', 'IC_ELIM', NULL, 'PC1001', 'SEG01',
 'SEG02', 'PROD_A', 'HARDWARE', '1000', 'SALES', NULL, 'PC2001', 'CO',
 -200.000, -200.000, 'PC', -50000.00, -50000.00, 'EUR'),

('1000', 'ACTUAL', '2024001', 'K4', '2000', '001000', 'G5100000',
 'AMER', 'EMEA', 'CAGR', '5100000', 'IC_ELIM', NULL, 'PC2001', 'SEG02',
 'SEG01', 'PROD_A', 'HARDWARE', '2000', 'COGS', NULL, 'PC1001', 'CO',
 -200.000, -200.000, 'PC', -50000.00, -50000.00, 'EUR'),

-- Budget version entries
(NULL, 'BUDGET', '2024001', 'K4', '1000', NULL, 'G4000000',
 'EMEA', NULL, 'CAGR', '4000000', 'REV', NULL, 'PC1001', 'SEG01',
 NULL, 'PROD_A', 'HARDWARE', '1000', 'SALES', NULL, NULL, 'BP',
 450.000, 450.000, 'PC', 112500.00, 112500.00, 'EUR'),

(NULL, 'BUDGET', '2024002', 'K4', '1000', NULL, 'G4000000',
 'EMEA', NULL, 'CAGR', '4000000', 'REV', NULL, 'PC1001', 'SEG01',
 NULL, 'PROD_B', 'SOFTWARE', '1000', 'SALES', NULL, NULL, 'BP',
 1000.000, 550.000, 'PC', 275000.00, 162500.00, 'EUR'),

(NULL, 'BUDGET', '2024003', 'K4', '1000', NULL, 'G4000000',
 'EMEA', NULL, 'CAGR', '4000000', 'REV', NULL, 'PC1001', 'SEG01',
 NULL, 'PROD_A', 'HARDWARE', '1000', 'SALES', NULL, NULL, 'BP',
 1500.000, 500.000, 'PC', 400000.00, 125000.00, 'EUR'),

-- Forecast version
(NULL, 'FORECAST', '2024001', 'K4', '1000', NULL, 'G4000000',
 'EMEA', NULL, 'CAGR', '4000000', 'REV', NULL, 'PC1001', 'SEG01',
 NULL, 'PROD_A', 'HARDWARE', '1000', 'SALES', NULL, NULL, 'FC',
 520.000, 520.000, 'PC', 130000.00, 130000.00, 'EUR');

-- ============================================================================
-- bpc_reporting - BPC consolidated reporting data
-- Final reporting layer with group currency translation
-- ============================================================================

INSERT INTO bpc_reporting (
    version, scope, fiscper, fiscvarnt, compcode, pc_area, ppc_area, pcompcd,
    grpacct, funcarea, spec, dsource, cs_trn_lc, cs_trn_gc
) VALUES
-- Actual consolidated results - Company 1000
('ACTUAL', 'CONSOL', '2024001', 'K4', '1000', 'EMEA', NULL, NULL,
 'G4000000', 'SALES', 'REVENUE', 'FI_DATA', 125000.00, 125000.00),

('ACTUAL', 'CONSOL', '2024001', 'K4', '1000', 'EMEA', NULL, NULL,
 'G5000000', 'COGS', 'COGS', 'FI_DATA', 75000.00, 75000.00),

('ACTUAL', 'CONSOL', '2024001', 'K4', '1000', 'EMEA', NULL, NULL,
 'G6200000', 'ADMIN', 'PERSONNEL', 'FI_DATA', 45000.00, 45000.00),

('ACTUAL', 'CONSOL', '2024001', 'K4', '1000', 'EMEA', NULL, NULL,
 'G6300000', 'ADMIN', 'OPEX', 'FI_DATA', 8500.00, 8500.00),

('ACTUAL', 'CONSOL', '2024001', 'K4', '1000', 'EMEA', NULL, NULL,
 'G6100000', 'RND', 'OPEX', 'FI_DATA', 35000.00, 35000.00),

('ACTUAL', 'CONSOL', '2024001', 'K4', '1000', 'EMEA', NULL, NULL,
 'G6400000', 'ADMIN', 'DEPR', 'FI_DATA', 12500.00, 12500.00),

-- Company 2000 (US) with currency translation (USD to EUR)
('ACTUAL', 'CONSOL', '2024001', 'K4', '2000', 'AMER', NULL, NULL,
 'G4000000', 'SALES', 'REVENUE', 'FI_DATA', 95000.00, 86363.64),

-- Company 3000 (UK) with currency translation (GBP to EUR)
('ACTUAL', 'CONSOL', '2024001', 'K4', '3000', 'EMEA', NULL, NULL,
 'G4000000', 'SALES', 'REVENUE', 'FI_DATA', 78000.00, 90697.67),

-- IC Elimination at group level
('ACTUAL', 'CONSOL', '2024001', 'K4', '1000', 'EMEA', 'AMER', '2000',
 'G4100000', 'SALES', 'IC_ELIM', 'CO_DATA', -50000.00, -50000.00),

('ACTUAL', 'CONSOL', '2024001', 'K4', '2000', 'AMER', 'EMEA', '1000',
 'G5100000', 'COGS', 'IC_ELIM', 'CO_DATA', -50000.00, -45454.55),

-- February data
('ACTUAL', 'CONSOL', '2024002', 'K4', '1000', 'EMEA', NULL, NULL,
 'G4000000', 'SALES', 'REVENUE', 'FI_DATA', 180000.00, 180000.00),

-- March data
('ACTUAL', 'CONSOL', '2024003', 'K4', '1000', 'EMEA', NULL, NULL,
 'G4000000', 'SALES', 'REVENUE', 'FI_DATA', 145000.00, 145000.00),

-- Budget version
('BUDGET', 'PLAN', '2024001', 'K4', '1000', 'EMEA', NULL, NULL,
 'G4000000', 'SALES', 'REVENUE', 'BPC_PLAN', 112500.00, 112500.00),

('BUDGET', 'PLAN', '2024001', 'K4', '1000', 'EMEA', NULL, NULL,
 'G5000000', 'COGS', 'COGS', 'BPC_PLAN', 67500.00, 67500.00),

('BUDGET', 'PLAN', '2024001', 'K4', '1000', 'EMEA', NULL, NULL,
 'G6200000', 'ADMIN', 'PERSONNEL', 'BPC_PLAN', 42000.00, 42000.00),

('BUDGET', 'PLAN', '2024002', 'K4', '1000', 'EMEA', NULL, NULL,
 'G4000000', 'SALES', 'REVENUE', 'BPC_PLAN', 162500.00, 162500.00),

('BUDGET', 'PLAN', '2024003', 'K4', '1000', 'EMEA', NULL, NULL,
 'G4000000', 'SALES', 'REVENUE', 'BPC_PLAN', 125000.00, 125000.00),

-- Forecast version
('FORECAST', 'FCST', '2024001', 'K4', '1000', 'EMEA', NULL, NULL,
 'G4000000', 'SALES', 'REVENUE', 'BPC_FCST', 130000.00, 130000.00),

('FORECAST', 'FCST', '2024002', 'K4', '1000', 'EMEA', NULL, NULL,
 'G4000000', 'SALES', 'REVENUE', 'BPC_FCST', 185000.00, 185000.00),

('FORECAST', 'FCST', '2024003', 'K4', '1000', 'EMEA', NULL, NULL,
 'G4000000', 'SALES', 'REVENUE', 'BPC_FCST', 150000.00, 150000.00),

-- Manual adjustments
('ACTUAL', 'CONSOL', '2024001', 'K4', 'CORP', 'GROUP', NULL, NULL,
 'G7000000', 'FIN', 'FX_ADJ', 'MANUAL', 2500.00, 2500.00),

('ACTUAL', 'CONSOL', '2024001', 'K4', 'CORP', 'GROUP', NULL, NULL,
 'G7100000', 'FIN', 'CONS_ADJ', 'MANUAL', -1200.00, -1200.00);

-- ============================================================================
-- DUPLICATE TRANSACTIONS SCENARIO - December 2024 (Period 012)
-- This simulates a data quality issue where invoices were loaded twice
-- due to a delta load failure causing a full reload with existing data
-- ============================================================================

-- Company 1000 - December duplicate invoice postings
-- Invoice 5000001 - ABC Corp (DUPLICATED - loaded twice)
INSERT INTO fi_reporting (
    fiscper, fiscvarnt, ac_docln, acledger, ac_docnr, rectype, version, compcode,
    custpsg, salesorg, division, distchan, pst_date, calyear, calmonth, fiscyear,
    chrt_acs, gl_acct, ac_docno, doc_date, ac_doctp, prof_ctr, segment,
    funcarea, customer, material, fidbcrin, curkey_lc, cs_trn_lc, amnt_dc,
    doc_currcy, quantity, unit, postxt
) VALUES
-- First occurrence of Invoice 5000001 (original load)
('2024012', 'K4', '001', '0L', '5000001', '0', 'ACTUAL', '1000',
 'CUST_ABC', '1000', '01', '10', '2024-12-15', '2024', '202412', '2024',
 'CAGR', '4000000', '5000001', '2024-12-15', 'DR', 'PC1001', 'SEG01',
 'SALES', 'CUST_ABC', 'MAT001', 'S', 'EUR', 50000.00, 50000.00,
 'EUR', 200.000, 'PC', 'Invoice ABC Corp - Product A'),

('2024012', 'K4', '002', '0L', '5000001', '0', 'ACTUAL', '1000',
 'CUST_ABC', '1000', '01', '10', '2024-12-15', '2024', '202412', '2024',
 'CAGR', '1400000', '5000001', '2024-12-15', 'DR', 'PC1001', 'SEG01',
 'SALES', 'CUST_ABC', 'MAT001', 'H', 'EUR', -50000.00, -50000.00,
 'EUR', -200.000, 'PC', 'AR - Invoice ABC Corp'),

-- DUPLICATE: Second occurrence of Invoice 5000001 (reload due to delta failure)
('2024012', 'K4', '001', '0L', '5000001', '1', 'ACTUAL', '1000',
 'CUST_ABC', '1000', '01', '10', '2024-12-15', '2024', '202412', '2024',
 'CAGR', '4000000', '5000001', '2024-12-15', 'DR', 'PC1001', 'SEG01',
 'SALES', 'CUST_ABC', 'MAT001', 'S', 'EUR', 50000.00, 50000.00,
 'EUR', 200.000, 'PC', 'Invoice ABC Corp - Product A'),

('2024012', 'K4', '002', '0L', '5000001', '1', 'ACTUAL', '1000',
 'CUST_ABC', '1000', '01', '10', '2024-12-15', '2024', '202412', '2024',
 'CAGR', '1400000', '5000001', '2024-12-15', 'DR', 'PC1001', 'SEG01',
 'SALES', 'CUST_ABC', 'MAT001', 'H', 'EUR', -50000.00, -50000.00,
 'EUR', -200.000, 'PC', 'AR - Invoice ABC Corp'),

-- Invoice 5000002 - XYZ Inc (DUPLICATED - loaded twice)
-- First occurrence
('2024012', 'K4', '001', '0L', '5000002', '0', 'ACTUAL', '1000',
 'CUST_XYZ', '1000', '01', '10', '2024-12-20', '2024', '202412', '2024',
 'CAGR', '4000000', '5000002', '2024-12-20', 'DR', 'PC1001', 'SEG01',
 'SALES', 'CUST_XYZ', 'MAT002', 'S', 'EUR', 25000.00, 25000.00,
 'EUR', 100.000, 'PC', 'Invoice XYZ Inc - Product B'),

('2024012', 'K4', '002', '0L', '5000002', '0', 'ACTUAL', '1000',
 'CUST_XYZ', '1000', '01', '10', '2024-12-20', '2024', '202412', '2024',
 'CAGR', '1400000', '5000002', '2024-12-20', 'DR', 'PC1001', 'SEG01',
 'SALES', 'CUST_XYZ', 'MAT002', 'H', 'EUR', -25000.00, -25000.00,
 'EUR', -100.000, 'PC', 'AR - Invoice XYZ Inc'),

-- DUPLICATE: Second occurrence of Invoice 5000002
('2024012', 'K4', '001', '0L', '5000002', '1', 'ACTUAL', '1000',
 'CUST_XYZ', '1000', '01', '10', '2024-12-20', '2024', '202412', '2024',
 'CAGR', '4000000', '5000002', '2024-12-20', 'DR', 'PC1001', 'SEG01',
 'SALES', 'CUST_XYZ', 'MAT002', 'S', 'EUR', 25000.00, 25000.00,
 'EUR', 100.000, 'PC', 'Invoice XYZ Inc - Product B'),

('2024012', 'K4', '002', '0L', '5000002', '1', 'ACTUAL', '1000',
 'CUST_XYZ', '1000', '01', '10', '2024-12-20', '2024', '202412', '2024',
 'CAGR', '1400000', '5000002', '2024-12-20', 'DR', 'PC1001', 'SEG01',
 'SALES', 'CUST_XYZ', 'MAT002', 'H', 'EUR', -25000.00, -25000.00,
 'EUR', -100.000, 'PC', 'AR - Invoice XYZ Inc'),

-- Invoice 5000003 - DEF Ltd (NOT duplicated - clean data for comparison)
('2024012', 'K4', '001', '0L', '5000003', '0', 'ACTUAL', '1000',
 'CUST_DEF', '1000', '01', '10', '2024-12-22', '2024', '202412', '2024',
 'CAGR', '4000000', '5000003', '2024-12-22', 'DR', 'PC1001', 'SEG01',
 'SALES', 'CUST_DEF', 'MAT001', 'S', 'EUR', 35000.00, 35000.00,
 'EUR', 140.000, 'PC', 'Invoice DEF Ltd - Product A'),

('2024012', 'K4', '002', '0L', '5000003', '0', 'ACTUAL', '1000',
 'CUST_DEF', '1000', '01', '10', '2024-12-22', '2024', '202412', '2024',
 'CAGR', '1400000', '5000003', '2024-12-22', 'DR', 'PC1001', 'SEG01',
 'SALES', 'CUST_DEF', 'MAT001', 'H', 'EUR', -35000.00, -35000.00,
 'EUR', -140.000, 'PC', 'AR - Invoice DEF Ltd');

-- December COGS entries (also duplicated to show full impact)
INSERT INTO fi_reporting (
    fiscper, fiscvarnt, ac_docln, acledger, ac_docnr, rectype, version, compcode,
    pst_date, calyear, calmonth, fiscyear, chrt_acs, gl_acct, ac_docno, doc_date,
    ac_doctp, prof_ctr, segment, funcarea, material, fidbcrin, curkey_lc,
    cs_trn_lc, amnt_dc, doc_currcy, quantity, unit, postxt
) VALUES
-- COGS for Invoice 5000001 (original)
('2024012', 'K4', '001', '0L', '5000101', '0', 'ACTUAL', '1000',
 '2024-12-15', '2024', '202412', '2024', 'CAGR', '5000000', '5000101', '2024-12-15',
 'SA', 'PC1001', 'SEG01', 'COGS', 'MAT001', 'S', 'EUR',
 30000.00, 30000.00, 'EUR', 200.000, 'PC', 'COGS - ABC Corp order'),

('2024012', 'K4', '002', '0L', '5000101', '0', 'ACTUAL', '1000',
 '2024-12-15', '2024', '202412', '2024', 'CAGR', '1300000', '5000101', '2024-12-15',
 'SA', 'PC1001', 'SEG01', 'COGS', 'MAT001', 'H', 'EUR',
 -30000.00, -30000.00, 'EUR', -200.000, 'PC', 'Inventory - ABC Corp'),

-- COGS for Invoice 5000001 (DUPLICATE)
('2024012', 'K4', '001', '0L', '5000101', '1', 'ACTUAL', '1000',
 '2024-12-15', '2024', '202412', '2024', 'CAGR', '5000000', '5000101', '2024-12-15',
 'SA', 'PC1001', 'SEG01', 'COGS', 'MAT001', 'S', 'EUR',
 30000.00, 30000.00, 'EUR', 200.000, 'PC', 'COGS - ABC Corp order'),

('2024012', 'K4', '002', '0L', '5000101', '1', 'ACTUAL', '1000',
 '2024-12-15', '2024', '202412', '2024', 'CAGR', '1300000', '5000101', '2024-12-15',
 'SA', 'PC1001', 'SEG01', 'COGS', 'MAT001', 'H', 'EUR',
 -30000.00, -30000.00, 'EUR', -200.000, 'PC', 'Inventory - ABC Corp');

-- Add December consolidation data (showing the DOUBLED amounts from duplicates)
INSERT INTO consolidation_mart (
    pcompcd, version, fiscper, fiscvarnt, compcode, pcompany, grpacct,
    pc_area, ppc_area, chrt_acs, gl_acct, spec, move_tp, prof_ctr, segment,
    psegment, prodh1, prodh2, co_area, funcarea, bwtar, part_pc, bpc_src,
    cs_ytd_qty, cs_trn_qty, unit, cs_ytd_lc, cs_trn_lc, curkey_lc
) VALUES
-- December Revenue - DOUBLED due to duplicate transactions
-- Expected: 110,000 EUR (50k + 25k + 35k), Actual in FI: 220,000 EUR
(NULL, 'ACTUAL', '2024012', 'K4', '1000', NULL, 'G4000000',
 'EMEA', NULL, 'CAGR', '4000000', 'REV', NULL, 'PC1001', 'SEG01',
 NULL, 'MIXED', 'MIXED', '1000', 'SALES', NULL, NULL, 'FI',
 880.000, 880.000, 'PC', 670000.00, 220000.00, 'EUR'),

-- December COGS - Also doubled for consistency
(NULL, 'ACTUAL', '2024012', 'K4', '1000', NULL, 'G5000000',
 'EMEA', NULL, 'CAGR', '5000000', 'COGS', NULL, 'PC1001', 'SEG01',
 NULL, 'MIXED', 'MIXED', '1000', 'COGS', NULL, NULL, 'FI',
 400.000, 400.000, 'PC', 135000.00, 60000.00, 'EUR');

-- Add December BPC data (also shows doubled amounts propagated)
INSERT INTO bpc_reporting (
    version, scope, fiscper, fiscvarnt, compcode, pc_area, ppc_area, pcompcd,
    grpacct, funcarea, spec, dsource, cs_trn_lc, cs_trn_gc
) VALUES
-- December actual - DOUBLED amounts from FI duplicates
('ACTUAL', 'CONSOL', '2024012', 'K4', '1000', 'EMEA', NULL, NULL,
 'G4000000', 'SALES', 'REVENUE', 'FI_DATA', 220000.00, 220000.00),

('ACTUAL', 'CONSOL', '2024012', 'K4', '1000', 'EMEA', NULL, NULL,
 'G5000000', 'COGS', 'COGS', 'FI_DATA', 60000.00, 60000.00),

-- December budget (correct amounts - no duplicates in planning)
('BUDGET', 'PLAN', '2024012', 'K4', '1000', 'EMEA', NULL, NULL,
 'G4000000', 'SALES', 'REVENUE', 'BPC_PLAN', 110000.00, 110000.00),

('BUDGET', 'PLAN', '2024012', 'K4', '1000', 'EMEA', NULL, NULL,
 'G5000000', 'COGS', 'COGS', 'BPC_PLAN', 30000.00, 30000.00);

-- ============================================================================
-- DUPLICATE TRANSACTIONS SCENARIO SUMMARY:
-- Company: 1000 (Germany/HQ)
-- Period: 2024012 (December 2024)
-- Issue: Delta load failure caused full reload, duplicating 2 of 3 invoices
--
-- Expected December Revenue: 110,000 EUR
--   - Invoice 5000001 (ABC Corp): 50,000 EUR
--   - Invoice 5000002 (XYZ Inc): 25,000 EUR
--   - Invoice 5000003 (DEF Ltd): 35,000 EUR
--
-- Actual in Database: 220,000 EUR (doubled due to duplicates)
--   - Invoice 5000001: 50,000 x 2 = 100,000 EUR
--   - Invoice 5000002: 25,000 x 2 = 50,000 EUR
--   - Invoice 5000003: 35,000 EUR (not duplicated)
--   - Total: 185,000 EUR in duplicated invoices + 35,000 = 220,000 EUR
--
-- Detection method:
--   1. Use get_fi_transactions for period 012 - notice high transaction count
--   2. Use get_fi_summary grouped by ac_docnr - see duplicate doc numbers
--   3. Compare actual vs budget - see 100% variance (220k vs 110k budget)
--   4. Use compare_sources - see FI doubled vs expected
-- ============================================================================

-- ============================================================================
-- Summary of test data:
-- - 3 company codes: 1000 (Germany/HQ), 2000 (US), 3000 (UK)
-- - 3 versions: ACTUAL, BUDGET, FORECAST
-- - Fiscal periods: 2024001-2024003 (Jan-Mar 2024)
-- - Includes intercompany transactions and eliminations
-- - Multiple currencies: EUR, USD, GBP
-- - Multiple functional areas: SALES, COGS, ADMIN, RND
-- - Multiple data sources: FI_DATA, CO_DATA, BPC_PLAN, BPC_FCST, MANUAL
-- ============================================================================
