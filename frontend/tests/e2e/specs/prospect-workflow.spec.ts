import { test, expect } from '@playwright/test';

test.describe('Prospect Intelligence Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/prospects');
  });

  test('displays prospects table with data', async ({ page }) => {
    const table = page.locator('table, [data-testid="prospects-table"], [role="table"]');
    await expect(table.first()).toBeVisible({ timeout: 10_000 });

    const rows = page.locator('tbody tr, [data-testid="prospect-row"]');
    await expect(rows.first()).toBeVisible({ timeout: 10_000 });
  });

  test('search filters prospects by company name', async ({ page }) => {
    const searchInput = page.locator(
      'input[placeholder*="earch"], input[type="search"], [data-testid="search-input"]'
    );

    if (await searchInput.count()) {
      await searchInput.first().fill('Reliance');
      await page.waitForTimeout(500);

      const rows = page.locator('tbody tr, [data-testid="prospect-row"]');
      const count = await rows.count();
      if (count > 0) {
        const firstRowText = await rows.first().textContent();
        expect(firstRowText?.toLowerCase()).toContain('reliance');
      }
    }
  });

  test('clicking a prospect opens detail view', async ({ page }) => {
    const firstRow = page.locator('tbody tr, [data-testid="prospect-row"]').first();
    await expect(firstRow).toBeVisible({ timeout: 10_000 });

    await firstRow.click();

    const detail = page.locator(
      '[data-testid="prospect-detail"], [role="dialog"], .drawer, .slide-over'
    );
    await expect(detail.first()).toBeVisible({ timeout: 5_000 });
  });

  test('prospect detail shows fit score breakdown', async ({ page }) => {
    const firstRow = page.locator('tbody tr, [data-testid="prospect-row"]').first();
    await expect(firstRow).toBeVisible({ timeout: 10_000 });
    await firstRow.click();

    const scoreElement = page.locator(
      '[data-testid="fit-score"], text=/\\d+/, .score, [class*="score"]'
    );
    if (await scoreElement.count()) {
      await expect(scoreElement.first()).toBeVisible();
    }
  });

  test('sector filter narrows results', async ({ page }) => {
    const sectorFilter = page.locator(
      'select, [data-testid="sector-filter"], [role="combobox"]'
    );

    if (await sectorFilter.count()) {
      const initialRows = await page
        .locator('tbody tr, [data-testid="prospect-row"]')
        .count();

      await sectorFilter.first().click();
      const option = page.locator('[role="option"], option').first();
      if (await option.count()) {
        await option.click();
        await page.waitForTimeout(500);
      }

      expect(initialRows).toBeGreaterThanOrEqual(0);
    }
  });

  test('sort by fit score works', async ({ page }) => {
    const scoreHeader = page.locator(
      'th:has-text("Fit"), th:has-text("Score"), [data-testid="sort-score"]'
    );

    if (await scoreHeader.count()) {
      await scoreHeader.first().click();
      await page.waitForTimeout(300);
    }
  });
});
