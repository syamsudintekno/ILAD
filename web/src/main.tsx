import { onIdTokenChanged, signInWithEmailAndPassword, signOut, type User } from '@firebase/auth';
import { useEffect, useState, type FormEvent } from 'react';
import { createRoot } from 'react-dom/client';
import { ApiError, quartiles, requestRun, type Overview, type Run } from './api';
import { auth, persistence } from './firebase';
import './styles.css';
import { InstitutionalResults } from './InstitutionalAnalytics';
import { DistributionComparison } from './DistributionComparison';
import { LecturerProfiles } from './LecturerProfiles';

const rpiFormat = new Intl.NumberFormat('id-ID', { maximumFractionDigits: 2 });
const maxFileSize = 2 * 1024 * 1024;

function Login() {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    if (!auth) return;
    setBusy(true);
    setError('');
    try {
      await persistence;
      await signInWithEmailAndPassword(auth, String(form.get('email')), String(form.get('password')));
    } catch {
      setError('Akun tidak dapat masuk. Periksa email dan kata sandi, lalu coba lagi.');
    } finally {
      setBusy(false);
    }
  }

  return <section className="card login">
    <p className="eyebrow">AKSES ADMIN QA</p>
    <h1>Masuk ke ILAD</h1>
    <p>Gunakan akun pilot untuk mengolah dan meninjau hasil EDOM sintetis.</p>
    <form onSubmit={submit}>
      <label>Email<input type="email" name="email" autoComplete="username" required /></label>
      <label>Kata sandi<input type="password" name="password" autoComplete="current-password" required /></label>
      {error && <p role="alert" className="notice error">{error}</p>}
      <button disabled={busy}>{busy ? 'Sedang masuk…' : 'Masuk'}</button>
    </form>
  </section>;
}

function Validation({ error }: { error: ApiError }) {
  const findings = error.validation?.findings;
  return <div className="notice error" role="alert">
    <strong>{error.message}</strong>
    {findings && <ul>
      {findings.missing_columns?.length ? <li>Kolom wajib yang belum ada: {findings.missing_columns.join(', ')}</li> : null}
      {findings.duplicate_row_count ? <li>Baris duplikat: {findings.duplicate_row_count}</li> : null}
      {Object.entries(findings.missing_values ?? {}).map(([column, count]) =>
        <li key={`missing-${column}`}>{column}: {count} nilai kosong</li>)}
      {Object.entries(findings.invalid_score_counts ?? {}).map(([column, count]) =>
        <li key={`invalid-${column}`}>{column}: {count} skor tidak valid</li>)}
    </ul>}
  </div>;
}

function Results({ overview }: { overview: Overview }) {
  const { kpis, top_lecturers: lecturers } = overview;
  const metrics = [
    ['Dosen', kpis.lecturer_count], ['Program studi', kpis.study_program_count],
    ['RPI rata-rata', kpis.average_rpi], ['RPI tertinggi', kpis.highest_rpi],
  ] as const;
  const largest = Math.max(1, ...Object.values(kpis.quartile_distribution));
  return <>
    <section className="metrics" aria-label="Ringkasan kohor">
      {metrics.map(([label, value]) => <div className="card metric" key={label}>
        <span>{label}</span><strong>{rpiFormat.format(value)}</strong>
      </div>)}
    </section>
    <section className="card">
      <h2>Distribusi kuartil</h2>
      <p>Jumlah dosen pada setiap kelompok RPI dalam kohor unggahan.</p>
      <ul className="chart">
        {quartiles.map((quartile) => {
          const count = kpis.quartile_distribution[quartile];
          return <li key={quartile}><span>{quartile}</span><span className="track" aria-hidden="true">
            <span style={{ width: `${(count / largest) * 100}%` }} />
          </span><strong>{count}</strong></li>;
        })}
      </ul>
    </section>
    <section className="card">
      <h2>10 dosen teratas</h2>
      <div className="table-wrap"><table>
        <thead><tr><th scope="col">Peringkat</th><th scope="col">Dosen</th><th scope="col">Program studi</th>
          <th scope="col">Skor EDOM</th><th scope="col">RPI</th><th scope="col">Kuartil</th></tr></thead>
        <tbody>{lecturers.map((row) => <tr key={row.lecturer_name}>
          <td>{row.rank}</td><th scope="row">{row.lecturer_name}</th><td>{row.study_program}</td>
          <td>{rpiFormat.format(row.overall_score)}</td><td>{rpiFormat.format(row.rpi)}</td><td>{row.quartile}</td>
        </tr>)}</tbody>
      </table></div>
    </section>
  </>;
}

function Dashboard({ user }: { user: User }) {
  const pages = { overview: 'Overview', institutional: 'Analitik Institusi', distribution: 'Distribusi', lecturer: 'Profil Dosen' } as const;
  const [page, setPage] = useState<keyof typeof pages>('overview');
  const storageKey = `ilad:last-run:${user.uid}`;
  const [runId, setRunId] = useState(() => sessionStorage.getItem(storageKey));
  const [run, setRun] = useState<Run | null>(null);
  const [selection, setSelection] = useState<{ file: File; key: string } | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!runId || (run?.run_id === runId && run.status !== 'processing')) return;
    const controller = new AbortController();
    const timeout = window.setTimeout(() => {
      void requestRun(user, `/${runId}`, { signal: controller.signal }).then(setRun).catch((failure) => {
        if (!controller.signal.aborted) setError(failure);
      });
    }, run?.run_id === runId ? 1500 : 0);
    return () => {
      window.clearTimeout(timeout);
      controller.abort();
    };
  }, [runId, run, user]);

  async function upload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selection || busy) return;
    if (selection.file.size > maxFileSize) {
      setError(new Error('Ukuran CSV maksimum 2 MiB.'));
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const result = await requestRun(user, '', {
        method: 'POST',
        headers: { 'Content-Type': 'text/csv', 'Idempotency-Key': selection.key },
        body: selection.file,
      });
      sessionStorage.setItem(storageKey, result.run_id);
      setRunId(result.run_id);
      setRun(result);
    } catch (failure) {
      setError(failure instanceof Error ? failure : new Error('Unggahan gagal.'));
    } finally {
      setBusy(false);
    }
  }

  const status = busy || (run?.status === 'processing' && !error) ? 'Sedang memproses CSV…'
    : run?.status === 'succeeded' ? 'Hasil analitik tersedia.'
    : run?.status === 'failed' ? 'Pemrosesan gagal. Coba unggah ulang.'
    : runId && !error ? 'Memuat hasil terakhir…' : '';

  return <div className="dashboard">
    <div className="page-heading">
      <div><p className="eyebrow">ANALITIK EDOM</p><h1>{pages[page]}</h1>
        <p>Skor dan peringkat RPI dihitung pada kohor dari satu unggahan.</p></div>
      <button type="button" className="secondary" disabled={busy} onClick={() => {
        if (auth) void signOut(auth).catch(() => setError(new Error('Tidak dapat keluar. Silakan coba lagi.')));
      }}>Keluar</button>
    </div>
    <nav className="page-switch" aria-label="Halaman analitik">
      <button type="button" className="secondary" aria-pressed={page === 'overview'} onClick={() => setPage('overview')}>Overview</button>
      <button type="button" className="secondary" aria-pressed={page === 'institutional'} onClick={() => setPage('institutional')}>Analitik Institusi</button>
      <button type="button" className="secondary" aria-pressed={page === 'distribution'} onClick={() => setPage('distribution')}>Distribusi</button>
      <button type="button" className="secondary" aria-pressed={page === 'lecturer'} onClick={() => setPage('lecturer')}>Profil Dosen</button>
    </nav>
    <section className="card" hidden={page !== 'overview'}>
      <h2>Unggah CSV EDOM</h2>
      <p>Gunakan data sintetis untuk pilot. Ukuran maksimum 2 MiB.</p>
      <form className="upload" onSubmit={upload}>
        <label>Berkas CSV<input type="file" accept=".csv,text/csv" disabled={busy} onChange={(event) => {
          const file = event.currentTarget.files?.[0];
          setError(null);
          setSelection(file ? { file, key: crypto.randomUUID() } : null);
        }} /></label>
        <button disabled={!selection || busy}>Proses CSV</button>
      </form>
      <p role="status">{status}</p>
      {error instanceof ApiError ? <Validation error={error} />
        : error ? <p className="notice error" role="alert">{error.message}</p> : null}
    </section>
    {page === 'overview' && run?.overview && <Results overview={run.overview} />}
    {page === 'institutional' && (run?.overview && run.institutional_analytics
      ? <InstitutionalResults analytics={run.institutional_analytics} kpis={run.overview.kpis} />
      : <p className="notice">{run?.overview
        ? 'Unggah ulang CSV di Overview untuk membuat statistik bagi run ini.'
        : 'Unggah dan proses CSV di Overview untuk melihat analitik institusi.'}</p>)}
    {page === 'distribution' && (run?.distribution
      ? <DistributionComparison {...run.distribution} />
      : <p className="notice">Unggah dan proses CSV di Overview untuk melihat perbandingan distribusi.</p>)}
    {page === 'lecturer' && (run?.lecturer_profiles
      ? <LecturerProfiles key={run.run_id} profiles={run.lecturer_profiles} />
      : <p className="notice">Unggah dan proses CSV di Overview untuk melihat profil dosen.</p>)}
  </div>;
}

function App() {
  const [session, setSession] = useState<{ user: User; admin: boolean } | null | undefined>(undefined);
  const [authError, setAuthError] = useState(false);
  useEffect(() => {
    if (!auth) return;
    const client = auth;
    let active = true;
    let revision = 0;
    const unsubscribe = onIdTokenChanged(client, (user) => {
      const currentRevision = ++revision;
      setAuthError(false);
      if (!user) {
        setSession(null);
        return;
      }
      void user.getIdTokenResult().then(({ claims }) => {
        if (active && revision === currentRevision) {
          setSession({ user, admin: claims.ilad_role === 'admin_qa' });
        }
      }).catch(() => {
        if (active && revision === currentRevision) setAuthError(true);
      });
    }, () => setAuthError(true));
    void persistence.catch(() => { if (active) setAuthError(true); });
    return () => {
      active = false;
      unsubscribe();
    };
  }, []);
  function endSession() {
    if (auth) void signOut(auth).catch(() => setAuthError(true));
  }
  return <>
    <header className="site-header"><div><strong>ILAD</strong><span>Institutional Learning Analytics Dashboard</span></div></header>
    <main>
      {!auth ? <p className="notice" role="status">Konfigurasi Firebase dan URL API belum tersedia.</p>
        : authError ? <section className="card login">
          <p className="notice error" role="alert">Sesi tidak dapat dimuat. Masuk kembali untuk melanjutkan.</p>
          <button type="button" onClick={endSession}>Keluar</button>
        </section>
        : session === undefined ? <p className="notice" role="status">Memuat sesi…</p>
        : !session ? <Login />
        : session.admin ? <Dashboard key={session.user.uid} user={session.user} />
        : <section className="card login">
          <h1>Akses pilot dibatasi</h1><p>Akun ini belum diberi peran Admin QA.</p>
          <button type="button" onClick={endSession}>Keluar</button>
        </section>}
    </main>
  </>;
}

createRoot(document.getElementById('root')!).render(<App />);
