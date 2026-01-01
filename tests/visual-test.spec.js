import { test } from '@playwright/test';

test.describe('Visual Theme Tests', () => {
  test('capture dark and light mode screenshots', async ({ page }) => {
    await page.goto('/');

    // Wait for page to fully load
    await page.waitForLoadState('networkidle');
    await page.waitForSelector('#themeToggle');

    // Take screenshot of dark mode
    await page.screenshot({
      path: 'screenshots/dark-mode.png',
      fullPage: true
    });

    // Toggle to light mode
    const toggleButton = page.locator('#themeToggle');
    await toggleButton.click();

    // Wait a bit for theme transition
    await page.waitForTimeout(300);

    // Take screenshot of light mode
    await page.screenshot({
      path: 'screenshots/light-mode.png',
      fullPage: true
    });

    console.log('Screenshots saved to screenshots/ directory');
  });
});
