import type { User } from '@firebase/auth';
import { useState } from 'react';
import { downloadRunExport, quartiles, type Overview, type Run } from './api';
import { Distribution } from './InstitutionalAnalytics';

const number = new Intl.NumberFormat('id-ID', { maximumFractionDigits: 2 });

export function InstitutionalReport({ user, run, overview }: { user: User; run: Run; overview: Overview }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const { kpis } = overview;
  const topLecturers = (run.lecturer_profiles ?? overview.top_lecturers).slice(0, 20);
  const metrics = [
    ['Dosen', kpis.lecturer_count], ['Program studi', kpis.study_program_count],
    ['RPI rata-rata', kpis.average_rpi], ['RPI tertinggi', kpis.highest_rpi],
    ['RPI terendah', kpis.lowest_rpi],
  ] as const;

  async function download(format: 'csv' | 'json') {
    setBusy(true);
    setError('');
    try {
      await downloadRunExport(user, run.run_id, format);
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'Ekspor belum dapat diunduh.');
    } finally {
      setBusy(false);
    }
  }

  return <>
    <section className="metrics" aria-label="Ringkasan laporan">
      {metrics.map(([label, value]) => <div className="card metric" key={label}>
        <span>{label}</span><strong>{number.format(value)}</strong>
      </div>)}
    </section>
    <section className="card">
      <h2>{run.lecturer_profiles ? '20 dosen teratas' : '10 dosen teratas'}</h2>
      <div className="table-wrap"><table>
        <thead><tr><th scope="col">Peringkat</th><th scope="col">Dosen</th>
          <th scope="col">Program studi</th><th scope="col">RPI</th><th scope="col">Kuartil</th></tr></thead>
        <tbody>{topLecturers.map((row) => <tr key={row.lecturer_name}>
          <td>{row.rank}</td><th scope="row">{row.lecturer_name}</th>
          <td>{row.study_program}</td><td>{number.format(row.rpi)}</td><td>{row.quartile}</td>
        </tr>)}</tbody>
      </table></div>
    </section>
    <Distribution title="Distribusi kuartil" rows={quartiles.map((label) => [label, kpis.quartile_distribution[label]])} />
    <section className="card">
      <h2>Unduh laporan</h2>
      <div className="page-switch">
        <button type="button" disabled={busy || !run.csv_export_available} onClick={() => void download('csv')}>Unduh CSV analitik</button>
        <button type="button" disabled={busy} onClick={() => void download('json')}>Unduh JSON ringkasan KPI</button>
      </div>
      {busy && <p role="status">Menyiapkan unduhan…</p>}
      {!run.csv_export_available && <p>Proses ulang unggahan untuk mengaktifkan CSV analitik pada run ini.</p>}
      {error && <p className="notice error" role="alert">{error}</p>}
    </section>
  </>;
}
