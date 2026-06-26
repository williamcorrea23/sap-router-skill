---
name: sap-sac-test-automation
description: SAP Analytics Cloud Test Automation — browser-based Playwright tests, SAC story regression testing, input validation tests, planning process validation, CI/CD integration for SAC. Use when writing automated tests for SAC stories, validating SAC planning processes, or integrating SAC testing in CI/CD.
---

# SAP Analytics Cloud Test Automation

Automated testing of SAC stories and analytic applications with Playwright.

## Playwright Setup

```bash
npm init -y
npm install @playwright/test
npx playwright install chromium
```

## Basic SAC Test

```javascript
const { test, expect } = require('@playwright/test');

test('SAC story loads correctly', async ({ page }) => {
  await page.goto('https://<tenant>.sapanalytics.cloud/sap/fpa/ui/app.html#/story&/S/123');

  // Wait for story to render
  await page.waitForSelector('.sap-custom-tile-content', { timeout: 30000 });

  // Verify title
  const title = await page.textContent('.story-title');
  expect(title).toContain('Revenue Analysis');
});
```

## Input Validation Test

```javascript
test('Planning input validation', async ({ page }) => {
  await page.goto(planningUrl);

  // Click planning cell
  await page.click('[data-cell-id="CostCenter.CC001.Amount"]');

  // Enter invalid value
  await page.fill('input.edit-cell', '-100');
  await page.press('input.edit-cell', 'Enter');

  // Assert validation message
  const msg = await page.textContent('.validation-message');
  expect(msg).toContain('Amount must be positive');
});
```

## CI/CD Integration

```yaml
# .github/workflows/sac-tests.yml
name: SAC Regression Tests
on:
  schedule:
    - cron: '0 6 * * 1'  # Every Monday
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npx playwright test sac-tests/ --reporter=html
        env:
          SAC_USER: ${{ secrets.SAC_USER }}
          SAC_PASSWORD: ${{ secrets.SAC_PASSWORD }}
      - uses: actions/upload-artifact@v3
        with:
          name: test-report
          path: playwright-report/
```

## SAC-specific Gotchas
- SAC loads asynchronously — use waitForSelector, not sleep
- Story IDs change between SAC tenants
- Planning models need data actions to be unlocked before tests
- Use separate "TEST" version for automated planning tests
