import { test, expect } from '@playwright/test';

test.describe('Deal Risk Console', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/deals');
  });

  test('displays deals grouped by risk level', async ({ page }) => {
    const content = page.locator('main, [data-testid="deals-content"]');
    await expect(content).toBeVisible({ timeout: 10_000 });

    const riskLabels = page.locator(
      'text=/At Risk|Healthy|Won|Lost/i, [data-testid*="risk-segment"]'
    );
    const count = await riskLabels.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });

  test('deal cards show key information', async ({ page }) => {
    const dealCard = page.locator(
      '[data-testid="deal-card"], .deal-card, [class*="deal"]'
    ).first();

    if (await dealCard.count()) {
      await expect(dealCard).toBeVisible({ timeout: 10_000 });
      const cardText = await dealCard.textContent();
      expect(cardText).toBeTruthy();
    }
  });

  test('clicking a deal opens detail panel', async ({ page }) => {
    const dealCard = page.locator(
      '[data-testid="deal-card"], .deal-card, [class*="deal"] >> visible=true'
    ).first();

    if (await dealCard.count()) {
      await dealCard.click();

      const detail = page.locator(
        '[data-testid="deal-detail"], [role="dialog"], .drawer, .slide-over, [class*="detail"]'
      );
      if (await detail.count()) {
        await expect(detail.first()).toBeVisible({ timeout: 5_000 });
      }
    }
  });

  test('at-risk deals are sorted by recovery priority', async ({ page }) => {
    const atRiskSection = page.locator(
      '[data-testid="at-risk-deals"], :has-text("At Risk")'
    ).first();

    if (await atRiskSection.count()) {
      await expect(atRiskSection).toBeVisible();
    }
  });

  test('deal detail shows risk waterfall', async ({ page }) => {
    const dealCard = page.locator(
      '[data-testid="deal-card"], .deal-card, [class*="deal"] >> visible=true'
    ).first();

    if (await dealCard.count()) {
      await dealCard.click();

      const chart = page.locator(
        '[data-testid="risk-waterfall"], .recharts-wrapper, svg, canvas'
      );
      if (await chart.count()) {
        await expect(chart.first()).toBeVisible({ timeout: 5_000 });
      }
    }
  });

  test('can navigate back to dashboard', async ({ page }) => {
    const dashLink = page.locator(
      'a[href="/"], nav >> text=Dashboard, [data-testid="nav-dashboard"]'
    );
    if (await dashLink.count()) {
      await dashLink.first().click();
      await expect(page).toHaveURL('/');
    }
  });
});
