import { quartiles, statisticColumns, type InstitutionalAnalytics, type Overview } from './api';

const format = new Intl.NumberFormat('id-ID', { maximumFractionDigits: 2 });
const scoreLabels: Record<string, string> = {
  pedagogic: 'Pedagogik', professional: 'Profesional', personality: 'Kepribadian',
  social: 'Sosial', overall_score: 'Skor EDOM keseluruhan',
};

export function Distribution({ title, rows }: { title: string; rows: [string, number][] }) {
  const largest = Math.max(1, ...rows.map(([, count]) => count));
  return <section className="card">
    <h2>{title}</h2>
    <ul className="chart distribution">
      {rows.map(([label, count], index) => <li key={index}>
        <span>{label}</span>
        <span className="track" aria-hidden="true"><span style={{ width: `${count / largest * 100}%` }} /></span>
        <strong>{count}</strong>
      </li>)}
    </ul>
  </section>;
}

export function InstitutionalResults({ analytics, kpis }: {
  analytics: InstitutionalAnalytics;
  kpis: Overview['kpis'];
}) {
  const sd = analytics.statistics.find(({ score }) => score === 'overall_score')?.standard_deviation;
  const metrics = [
    ['Dosen', kpis.lecturer_count], ['Program studi', kpis.study_program_count],
    ['RPI rata-rata', kpis.average_rpi], ['Simpangan baku skor EDOM', sd],
    ['RPI tertinggi', kpis.highest_rpi], ['RPI terendah', kpis.lowest_rpi],
  ] as const;
  return <>
    <section className="metrics" aria-label="Ringkasan institusi">
      {metrics.map(([label, value]) => <div className="card metric" key={label}>
        <span>{label}</span><strong>{value == null ? '—' : format.format(value)}</strong>
      </div>)}
    </section>
    <section className="card">
      <h2>Statistik deskriptif</h2>
      <div className="table-wrap"><table>
        <thead><tr>{['Skor', 'Rata-rata', 'Median', 'Simpangan baku', 'Varians', 'Minimum', 'Maksimum']
          .map((label) => <th key={label} scope="col">{label}</th>)}</tr></thead>
        <tbody>{analytics.statistics.map((row) => <tr key={row.score}>
          <th scope="row">{scoreLabels[row.score] ?? row.score}</th>
          {statisticColumns.map((metric) => <td key={metric}>
            {row[metric] === null ? '—' : format.format(row[metric])}
          </td>)}
        </tr>)}</tbody>
      </table></div>
    </section>
    <Distribution title="Distribusi RPI (jumlah dosen)" rows={analytics.rpi_histogram.map(
      ({ lower, upper, count }) => [`${format.format(lower)}–${format.format(upper)}`, count],
    )} />
    <Distribution title="Distribusi kuartil" rows={quartiles.map((label) => [label, kpis.quartile_distribution[label]])} />
    <details className="card">
      <summary>Metodologi RPI</summary>
      <p>RPI membandingkan profil kompetensi dosen dalam satu kohor. Transformasi rankit mengubah peringkat tiap dimensi menjadi skor normal, lalu empat dimensi digabung dengan bobot sama dan diskalakan dengan rumus RPI = 50 + 10 × skor gabungan.</p>
    </details>
  </>;
}
