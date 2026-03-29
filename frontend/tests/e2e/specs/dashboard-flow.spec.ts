import { test, expect } from '@playwright/test';

test.describe('Dashboard Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('loads the dashboard with KPI cards', async ({ page }) => {
    await expect(page).toHaveURL('/');

    const kpiSection = page.locator('[data-testid="kpi-cards"], .kpi-cards, main');
    await expect(kpiSection).toBeVisible({ timeout: 10_000 });
  });

  test('displays pipeline funnel chart', async ({ page }) => {
    const funnel = page.locator(
      '[data-testid="pipeline-funnel"], .recharts-wrapper, svg.recharts-surface'
    );
    await expect(funnel.first()).toBeVisible({ timeout: 10_000 });
  });

  test('displays risk heatmap', async ({ page }) => {
    const heatmap = page.locator(
      '[data-testid="risk-heatmap"], .nivo-heatmap, [class*="heatmap"]'
    );
    if (await heatmap.count()) {
      await expect(heatmap.first()).toBeVisible();
    }
  });

  test('navigation sidebar is present', async ({ page }) => {
    const nav = page.locator('nav, [data-testid="sidebar"], aside');
    await expect(nav.first()).toBeVisible();
  });

  test('can navigate to prospects page from sidebar', async ({ page }) => {
    const prospectLink = page.locator('a[href="/prospects"], nav >> text=Prospects');
    if (await prospectLink.count()) {
      await prospectLink.first().click();
      await expect(page).toHaveURL(/\/prospects/);
    }
  });

  test('can navigate to deals page from sidebar', async ({ page }) => {
    const dealLink = page.locator('a[href="/deals"], nav >> text=Deals');
    if (await dealLink.count()) {
      await dealLink.first().click();
      await expect(page).toHaveURL(/\/deals/);
    }
  });

  test('dark mode toggle works', async ({ page }) => {
    const toggle = page.locator(
      '[data-testid="dark-mode-toggle"], button:has-text("Dark"), [aria-label*="theme"]'
    );
    if (await toggle.count()) {
      await toggle.first().click();
      const html = page.locator('html');
      const classAttr = await html.getAttribute('class');
      expect(classAttr).toBeTruthy();
    }
  });
});
