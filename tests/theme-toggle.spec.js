import { test, expect } from '@playwright/test';

test.describe('Theme Toggle Feature', () => {
  test.beforeEach(async ({ page }) => {
    // Clear localStorage before each test
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
    await page.reload();
  });

  test('theme toggle button is visible', async ({ page }) => {
    await page.goto('/');

    // Check if the theme toggle button exists
    const toggleButton = page.locator('#themeToggle');
    await expect(toggleButton).toBeVisible();

    // Verify button has correct aria-label for accessibility
    await expect(toggleButton).toHaveAttribute('aria-label', 'Toggle dark/light mode');
  });

  test('default theme is dark mode', async ({ page }) => {
    await page.goto('/');

    // Check the data-theme attribute on root element
    const htmlElement = page.locator('html');
    const theme = await htmlElement.getAttribute('data-theme');
    expect(theme).toBe('dark');

    // Verify dark mode icon (moon) is visible
    const moonIcon = page.locator('.theme-toggle .moon-icon');
    await expect(moonIcon).toBeVisible();

    // Verify light mode icon (sun) is hidden
    const sunIcon = page.locator('.theme-toggle .sun-icon');
    await expect(sunIcon).toBeHidden();
  });

  test('can toggle from dark to light mode', async ({ page }) => {
    await page.goto('/');

    const toggleButton = page.locator('#themeToggle');
    const htmlElement = page.locator('html');

    // Initially should be dark mode
    let theme = await htmlElement.getAttribute('data-theme');
    expect(theme).toBe('dark');

    // Click the toggle button
    await toggleButton.click();

    // Should now be light mode
    theme = await htmlElement.getAttribute('data-theme');
    expect(theme).toBe('light');

    // Verify sun icon is now visible
    const sunIcon = page.locator('.theme-toggle .sun-icon');
    await expect(sunIcon).toBeVisible();

    // Verify moon icon is now hidden
    const moonIcon = page.locator('.theme-toggle .moon-icon');
    await expect(moonIcon).toBeHidden();
  });

  test('can toggle from light to dark mode', async ({ page }) => {
    await page.goto('/');

    const toggleButton = page.locator('#themeToggle');
    const htmlElement = page.locator('html');

    // Toggle to light mode first
    await toggleButton.click();
    await expect(htmlElement).toHaveAttribute('data-theme', 'light');

    // Toggle back to dark mode
    await toggleButton.click();
    await expect(htmlElement).toHaveAttribute('data-theme', 'dark');

    // Verify moon icon is visible again
    const moonIcon = page.locator('.theme-toggle .moon-icon');
    await expect(moonIcon).toBeVisible();
  });

  test('theme preference persists in localStorage', async ({ page }) => {
    await page.goto('/');

    const toggleButton = page.locator('#themeToggle');

    // Toggle to light mode
    await toggleButton.click();

    // Check localStorage
    const storedTheme = await page.evaluate(() => localStorage.getItem('theme'));
    expect(storedTheme).toBe('light');
  });

  test('theme persists after page reload', async ({ page }) => {
    await page.goto('/');

    const toggleButton = page.locator('#themeToggle');
    const htmlElement = page.locator('html');

    // Toggle to light mode
    await toggleButton.click();
    await expect(htmlElement).toHaveAttribute('data-theme', 'light');

    // Reload the page
    await page.reload();

    // Theme should still be light
    await expect(htmlElement).toHaveAttribute('data-theme', 'light');
    const sunIcon = page.locator('.theme-toggle .sun-icon');
    await expect(sunIcon).toBeVisible();
  });

  test('theme toggle button has correct CSS styles', async ({ page }) => {
    await page.goto('/');

    const toggleButton = page.locator('#themeToggle');

    // Check button is positioned correctly
    const styles = await toggleButton.evaluate((el) => {
      const computed = window.getComputedStyle(el);
      return {
        position: computed.position,
        borderRadius: computed.borderRadius,
        cursor: computed.cursor,
      };
    });

    expect(styles.position).toBe('fixed');
    expect(styles.cursor).toBe('pointer');
  });

  test('CSS variables change when theme toggles', async ({ page }) => {
    await page.goto('/');

    const toggleButton = page.locator('#themeToggle');

    // Get dark mode background color
    const darkBg = await page.evaluate(() => {
      return getComputedStyle(document.documentElement).getPropertyValue('--background');
    });

    // Toggle to light mode
    await toggleButton.click();

    // Get light mode background color
    const lightBg = await page.evaluate(() => {
      return getComputedStyle(document.documentElement).getPropertyValue('--background');
    });

    // Colors should be different
    expect(darkBg.trim()).not.toBe(lightBg.trim());
    expect(darkBg.trim()).toBe('#0f172a'); // Dark background
    expect(lightBg.trim()).toBe('#f8fafc'); // Light background
  });

  test('multiple rapid toggles work correctly', async ({ page }) => {
    await page.goto('/');

    const toggleButton = page.locator('#themeToggle');
    const htmlElement = page.locator('html');

    // Toggle multiple times rapidly
    await toggleButton.click(); // -> light
    await toggleButton.click(); // -> dark
    await toggleButton.click(); // -> light
    await toggleButton.click(); // -> dark
    await toggleButton.click(); // -> light

    // Should end up in light mode
    await expect(htmlElement).toHaveAttribute('data-theme', 'light');

    const storedTheme = await page.evaluate(() => localStorage.getItem('theme'));
    expect(storedTheme).toBe('light');
  });

  test('theme button is accessible via keyboard', async ({ page }) => {
    await page.goto('/');

    const toggleButton = page.locator('#themeToggle');
    const htmlElement = page.locator('html');

    // Focus the button using Tab key
    await toggleButton.focus();

    // Verify button has focus
    const isFocused = await toggleButton.evaluate((el) => el === document.activeElement);
    expect(isFocused).toBeTruthy();

    // Press Enter to toggle
    await page.keyboard.press('Enter');

    // Theme should change
    await expect(htmlElement).toHaveAttribute('data-theme', 'light');
  });

  test('visual elements render correctly in both themes', async ({ page }) => {
    await page.goto('/');

    const toggleButton = page.locator('#themeToggle');

    // Check dark mode elements
    const sidebar = page.locator('.sidebar');
    await expect(sidebar).toBeVisible();

    const chatInput = page.locator('#chatInput');
    await expect(chatInput).toBeVisible();

    // Toggle to light mode
    await toggleButton.click();

    // Elements should still be visible in light mode
    await expect(sidebar).toBeVisible();
    await expect(chatInput).toBeVisible();
  });
});
