---
name: sap-sac-test-automation
description: >
  SAP Analytics Cloud Test Automation — Playwright-based browser tests for SAC stories,
  planning input validation, regression testing, and CI/CD integration. Use when writing
  automated tests for SAC stories, validating SAC planning processes, or integrating SAC
  testing into a CI/CD pipeline.
trigger:
  keywords:
    - SAC test automation
    - Playwright SAP Analytics Cloud
    - SAC story regression test
    - SAC planning validation
    - automated testing SAP analytics
  intent: User needs to automate browser-based tests against SAP Analytics Cloud stories, planning models, or analytic applications.
---

# SAP Analytics Cloud Test Automation

Automated testing of SAC stories and analytic applications using Playwright.

## Prerequisites

- Node.js 18+ installed
- Access to an SAP Analytics Cloud tenant (URL, user, password)
- Story or planning model deployed in the target SAC tenant
- (CI/CD) GitHub Actions or equivalent with `SAC_USER` and `SAC_PASSWORD` secrets

## 1. Install Playwright

```bash
npm init -y
npm install @playwright/test
npx playwright install chromium
```

## 2. Configure Playwright for SAC

```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test')

module.exports = defineConfig({
  testDir: './sac-tests',
  timeout: 60000,           // SAC loads are slow
  retries: 1,               // flaky SAC renders
  use: {
    headless: true,
    viewport: { width: 1920, height: 1080 },
    ignoreHTTPSErrors: true,
    storageState: 'sac-auth.json',  // pre-saved auth state
  },
})
```

## 3. Authenticate Once and Save State

```javascript
// sac-tests/auth-setup.js
const { test: setup } = require('@playwright/test')

setup('authenticate SAC', async ({ page }) => {
  await page.goto('https://<tenant>.sapanalytics.cloud')
  await page.fill('#USER', process.env.SAC_USER)
  await page.fill('#PASSWORD', process.env.SAC_PASSWORD)
  await page.click('[type="submit"]')
  await page.waitForURL('**/sap/fpa/ui/app.html**', { timeout: 30000 })
  await page.context().storageState({ path: 'sac-auth.json' })
})
```

## 4. Write a Story Regression Test

```javascript
// sac-tests/story-load.spec.js
const { test, expect } = require('@playwright/test')

test('Revenue Analysis story loads', async ({ page }) => {
  await page.goto(
    'https://<tenant>.sapanalytics.cloud/sap/fpa/ui/app.html#/story&/S/123'
  )

  // SAC renders asynchronously — always use waitForSelector, never sleep
  await page.waitForSelector('.sap-custom-tile-content', { timeout: 30000 })

  const title = await page.textContent('.story-title')
  expect(title).toContain('Revenue Analysis')
})
```

## 5. Write a Planning Input Validation Test

```javascript
// sac-tests/planning-validation.spec.js
const { test, expect } = require('@playwright/test')

test('Rejects negative planning amount', async ({ page }) => {
  await page.goto(planningUrl)

  // Click the planning cell
  await page.click('[data-cell-id="CostCenter.CC001.Amount"]')

  // Enter invalid value
  await page.fill('input.edit-cell', '-100')
  await page.press('input.edit-cell', 'Enter')

  // Assert validation message appears
  const msg = await page.textContent('.validation-message')
  expect(msg).toContain('Amount must be positive')
})
```

## 6. CI/CD Integration (GitHub Actions)

```yaml
# .github/workflows/sac-tests.yml
name: SAC Regression Tests
on:
  schedule:
    - cron: '0 6 * * 1'  # Every Monday
  workflow_dispatch:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npx playwright install chromium
      - run: npx playwright test --reporter=html
        env:
          SAC_USER: ${{ secrets.SAC_USER }}
          SAC_PASSWORD: ${{ secrets.SAC_PASSWORD }}
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-report
          path: playwright-report/
```

## Pitfalls

- **Cause:** Tests fail intermittently with timeout → **Solution:** SAC loads asynchronously; use `waitForSelector` with 30s timeout, never `page.waitForTimeout`.
- **Cause:** Story ID `S/123` works in dev but not prod → **Solution:** Story IDs differ between tenants; parameterize the story ID via env var `SAC_STORY_ID`.
- **Cause:** Planning tests corrupt production data → **Solution:** Use a separate `TEST` version in the planning model; never run automated tests against the `PUBLIC` version.
- **Cause:** Planning cells are read-only during test → **Solution:** Data actions must be unlocked before tests; add a setup step to unlock the model version.
- **Cause:** Auth dialog appears on every test → **Solution:** Use `storageState` to save and reuse the authenticated session across all tests.
- **Cause:** CI pipeline fails because Chromium not installed → **Solution:** Add `npx playwright install chromium` as an explicit CI step before running tests.

## Verification

```bash
# 1. Run tests locally and confirm pass
npx playwright test --reporter=list

# 2. Verify auth state file was created
test -f sac-auth.json && echo "Auth state OK" || echo "Auth state MISSING"

# 3. View HTML report
npx playwright show-report

# 4. In CI, check artifact upload
#    GitHub Actions → Artifacts → test-report → index.html
```
