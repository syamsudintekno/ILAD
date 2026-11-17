import { expect, test, type Page } from '@playwright/test';

const password = 'EmulatorOnly-ILAD-2026';
const admin = 'qa-browser@example.test';
const viewer = 'viewer-browser@example.test';
const indicators = Array.from({ length: 20 }, (_, index) => `P${index + 1}`);
const validCsv = [
  ['lecturer_name', 'study_program', 'faculty', ...indicators],
  ['Dosen Sintetis A', 'Prodi A', 'Fakultas A', ...Array(20).fill(5)],
  ['Dosen Sintetis B', 'Prodi B', 'Fakultas A', ...Array(20).fill(4)],
  ['Dosen Sintetis C', 'Prodi B', 'Fakultas A', ...Array(20).fill(4)],
].map((row) => row.join(',')).join('\n');

async function login(page: Page, email: string) {
  await page.goto('/');
  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Kata sandi').fill(password);
  await page.getByRole('button', { name: 'Masuk', exact: true }).click();
}

async function upload(page: Page, name: string, content: string) {
  await page.getByLabel('Berkas CSV').setInputFiles({
    name,
    mimeType: 'text/csv',
    buffer: Buffer.from(content),
  });
  await page.getByRole('button', { name: 'Proses CSV' }).click();
}

test('Admin QA validates input, reloads the Overview, and signs out', async ({ page }) => {
  await login(page, admin);
  await expect(page.getByRole('heading', { name: 'Overview' })).toBeVisible();

  await upload(page, 'invalid.csv', 'lecturer_name\nDosen Sintetis\n');
  await expect(page.getByRole('alert')).toContainText('Data CSV gagal divalidasi');
  await expect(page.getByRole('alert')).toContainText('Kolom wajib yang belum ada');

  await upload(page, 'valid.csv', validCsv);
  await expect(page.getByRole('status')).toHaveText('Hasil analitik tersedia.');
  await expect(page.getByRole('heading', { name: 'Distribusi kuartil' })).toBeVisible();
  await page.getByRole('button', { name: 'Distribusi', exact: true }).click();
  for (const heading of ['Histogram Skor EDOM', 'Histogram RPI', 'Boxplot Skor EDOM', 'Boxplot RPI']) {
    await expect(page.getByRole('heading', { name: heading, exact: true })).toBeVisible();
  }
  await expect(page.getByRole('row', { name: /^Median/ }).locator('td')).toHaveText(['4', '46,043']);
  const rows = page.getByRole('table').locator('tbody tr');
  const expected = [
    ['1', 'Dosen Sintetis A', 'Prodi A', '5', '58,69', 'Q1'],
    ['2', 'Dosen Sintetis B', 'Prodi B', '4', '46,04', 'Q2'],
    ['2', 'Dosen Sintetis C', 'Prodi B', '4', '46,04', 'Q2'],
  ];
  for (const [index, cells] of expected.entries()) {
    await expect(rows.nth(index).locator('th, td')).toHaveText(cells);
  }
  await expect(rows).toHaveCount(expected.length);

  await page.reload();
  await expect(page.getByRole('status')).toHaveText('Hasil analitik tersedia.');
  for (const [index, cells] of expected.entries()) {
    await expect(rows.nth(index).locator('th, td')).toHaveText(cells);
  }
  await page.getByRole('button', { name: 'Analitik Institusi' }).click();
  await expect(page.getByRole('row', { name: /Skor EDOM keseluruhan/ }).locator('td'))
    .toHaveText(['4,33', '4', '0,47', '0,22', '4', '5']);
  await expect(page.getByRole('heading', { name: 'Distribusi RPI (jumlah dosen)' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Distribusi kuartil' })).toBeVisible();
  await page.getByRole('button', { name: 'Keluar' }).click();
  await expect(page.getByRole('heading', { name: 'Masuk ke ILAD' })).toBeVisible();
});

test('signed-in viewer cannot see the upload or results', async ({ page }) => {
  await login(page, viewer);
  await expect(page.getByRole('heading', { name: 'Akses pilot dibatasi' })).toBeVisible();
  await expect(page.getByLabel('Berkas CSV')).toHaveCount(0);
  await expect(page.getByRole('table')).toHaveCount(0);
});
