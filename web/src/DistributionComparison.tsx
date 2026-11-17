import { distributionMetrics, type ScoreDistribution } from './api';
import { Distribution } from './InstitutionalAnalytics';

const format = new Intl.NumberFormat('id-ID', { maximumFractionDigits: 3 });
const labels = ['Rata-rata', 'Median', 'Simpangan baku', 'Varians', 'Minimum', 'Maksimum', 'Skewness', 'Kurtosis'];

function Boxplot({ title, data }: { title: string; data: ScoreDistribution }) {
  const { lower_whisker, q1, median, q3, upper_whisker, outlier_count } = data.boxplot;
  const minimum = data.statistics.minimum ?? lower_whisker;
  const maximum = data.statistics.maximum ?? upper_whisker;
  const position = (value: number) => maximum === minimum ? 50 : 100 * (value - minimum) / (maximum - minimum);
  const width = (from: number, to: number) => `${position(to) - position(from)}%`;
  return <section className="card">
    <h2>Boxplot {title}</h2>
    <div className="boxplot" aria-hidden="true">
      <span className="whisker" style={{ left: `${position(lower_whisker)}%`, width: width(lower_whisker, upper_whisker) }} />
      <span className="box" style={{ left: `${position(q1)}%`, width: width(q1, q3) }} />
      <span className="median" style={{ left: `${position(median)}%` }} />
    </div>
    <dl className="boxplot-values">
      {([['Whisker bawah', lower_whisker], ['Q1', q1], ['Median', median], ['Q3', q3],
        ['Whisker atas', upper_whisker], ['Pencilan', outlier_count]] as const)
        .map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{format.format(value)}</dd></div>)}
    </dl>
  </section>;
}

export function DistributionComparison({ edom, rpi }: Record<'edom' | 'rpi', ScoreDistribution>) {
  const series = [['Skor EDOM', edom], ['RPI', rpi]] as const;
  return <>
    <div className="comparison-grid">
      {series.map(([label, data]) => <Distribution key={label} title={`Histogram ${label}`}
        rows={data.histogram.map(({ lower, upper, count }) => [`${format.format(lower)}–${format.format(upper)}`, count])} />)}
      {series.map(([label, data]) => <Boxplot key={label} title={label} data={data} />)}
    </div>
    <section className="card">
      <h2>Statistik distribusi</h2>
      <div className="table-wrap"><table>
        <thead><tr><th scope="col">Statistik</th><th scope="col">Skor EDOM</th><th scope="col">RPI</th></tr></thead>
        <tbody>{distributionMetrics.map((metric, index) => <tr key={metric}>
          <th scope="row">{labels[index]}</th>
          {series.map(([label, data]) => {
            const value = data.statistics[metric];
            return <td key={label}>{value === null ? '—' : format.format(value)}</td>;
          })}
        </tr>)}</tbody>
      </table></div>
      <p>Grafik memakai skala masing-masing. Varians dan simpangan baku ditafsirkan dalam skala skor asal. Skewness dan kurtosis menggambarkan bentuk distribusi pada kohor ini.</p>
    </section>
  </>;
}
