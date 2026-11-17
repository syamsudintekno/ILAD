import { useState } from 'react';
import { lecturerDimensions, type LecturerProfile } from './api';

const format = new Intl.NumberFormat('id-ID', { maximumFractionDigits: 2 });
const dimensionLabels = {
  pedagogic: 'Pedagogik', professional: 'Profesional',
  personality: 'Kepribadian', social: 'Sosial',
};

export function LecturerProfiles({ profiles }: { profiles: LecturerProfile[] }) {
  const [selected, setSelected] = useState('');
  const profile = profiles.find(({ lecturer_name }) => lecturer_name === selected) ?? profiles[0];
  if (!profile) return <p className="notice">Kohor ini belum memiliki profil dosen.</p>;

  return <>
    <section className="card">
      <label>Pilih dosen
        <select value={profile.lecturer_name} onChange={(event) => setSelected(event.currentTarget.value)}>
          {profiles.map(({ lecturer_name }) => <option key={lecturer_name} value={lecturer_name}>{lecturer_name}</option>)}
        </select>
      </label>
      <h2>{profile.lecturer_name}</h2>
      <p>Program studi {profile.study_program}</p>
    </section>
    <section className="metrics" aria-label="Ringkasan profil dosen">
      <div className="card metric"><span>RPI</span><strong>{format.format(profile.rpi)}</strong></div>
      <div className="card metric"><span>Peringkat institusi</span><strong>{profile.rank}</strong></div>
      <div className="card metric"><span>Kuartil</span><strong>{profile.quartile}</strong></div>
    </section>
    <section className="card">
      <h2>Profil kompetensi</h2>
      <p>Skor tiap dimensi pada skala EDOM 1–5.</p>
      <div className="table-wrap"><table className="competency-table">
        <thead><tr><th scope="col">Dimensi</th><th scope="col">Skor</th></tr></thead>
        <tbody>{lecturerDimensions.map((dimension) => <tr key={dimension}>
          <th scope="row">{dimensionLabels[dimension]}</th>
          <td><div className="competency-score">
            <span className="track" aria-hidden="true">
              <span style={{ width: `${(profile[dimension] - 1) / 4 * 100}%` }} />
            </span>
            <strong>{format.format(profile[dimension])}</strong>
          </div></td>
        </tr>)}</tbody>
      </table></div>
    </section>
  </>;
}
