import type { User } from '@firebase/auth';
import { apiUrl } from './firebase';

export const quartiles = ['Q1', 'Q2', 'Q3', 'Q4'] as const;
type Quartile = typeof quartiles[number];

export interface Overview {
  kpis: {
    lecturer_count: number;
    study_program_count: number;
    average_rpi: number;
    lowest_rpi: number;
    highest_rpi: number;
    quartile_distribution: Record<Quartile, number>;
  };
  top_lecturers: {
    lecturer_name: string;
    study_program: string;
    overall_score: number;
    rpi: number;
    rank: number;
    quartile: Quartile;
  }[];
}

export interface Run {
  run_id: string;
  status: 'processing' | 'succeeded' | 'invalid' | 'failed';
  overview: Overview | null;
  institutional_analytics?: InstitutionalAnalytics;
  distribution?: Record<'edom' | 'rpi', ScoreDistribution>;
  lecturer_profiles?: LecturerProfile[];
  csv_export_available?: boolean;
  error?: { message: string };
  validation?: {
    findings: {
      missing_columns?: string[];
      duplicate_row_count?: number;
      missing_values?: Record<string, number>;
      invalid_score_counts?: Record<string, number>;
    };
  };
}

export const lecturerDimensions = ['pedagogic', 'professional', 'personality', 'social'] as const;
export type LecturerProfile = Pick<Overview['top_lecturers'][number],
  'lecturer_name' | 'study_program' | 'rpi' | 'rank' | 'quartile'
> & Record<typeof lecturerDimensions[number], number>;

export const statisticColumns = ['mean', 'median', 'standard_deviation', 'variance', 'minimum', 'maximum'] as const;
export const distributionMetrics = [...statisticColumns, 'skewness', 'kurtosis'] as const;

export interface ScoreDistribution {
  histogram: InstitutionalAnalytics['rpi_histogram'];
  statistics: Record<typeof distributionMetrics[number], number | null>;
  boxplot: {
    lower_whisker: number;
    q1: number;
    median: number;
    q3: number;
    upper_whisker: number;
    outlier_count: number;
  };
}

export interface InstitutionalAnalytics {
  statistics: (Record<typeof statisticColumns[number], number | null> & { score: string })[];
  rpi_histogram: { lower: number; upper: number; count: number }[];
}

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly validation?: Run['validation'],
  ) {
    super(message);
  }
}

export async function requestRun(
  user: User,
  path: string,
  options: RequestInit = {},
): Promise<Run> {
  const headers = new Headers(options.headers);
  headers.set('Authorization', `Bearer ${await user.getIdToken()}`);
  const response = await fetch(`${apiUrl}/v1/runs${path}`, { ...options, headers });
  const data = await response.json().catch(() => null);
  if (!response.ok || !data) {
    throw new ApiError(
      data?.error?.message ?? 'Layanan ILAD belum dapat dihubungi.',
      response.status,
      data?.validation,
    );
  }
  return data as Run;
}

export async function downloadRunExport(user: User, runId: string, format: 'csv' | 'json') {
  const response = await fetch(`${apiUrl}/v1/runs/${runId}/exports/${format}`, {
    headers: { Authorization: `Bearer ${await user.getIdToken()}` },
  });
  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new ApiError(data?.error?.message ?? 'Ekspor belum dapat diunduh.', response.status);
  }
  const url = URL.createObjectURL(await response.blob());
  const link = document.createElement('a');
  link.href = url;
  link.download = format === 'csv' ? 'ilad_analytics.csv' : 'ilad_kpi_summary.json';
  link.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}
