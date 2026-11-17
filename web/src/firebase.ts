import { initializeApp } from '@firebase/app';
import { browserSessionPersistence, connectAuthEmulator, getAuth, setPersistence } from '@firebase/auth';

const env = import.meta.env;
const useEmulator = env.DEV && env.VITE_USE_FIREBASE_EMULATOR === 'true';
const projectId: string | undefined = env.VITE_FIREBASE_PROJECT_ID?.trim();

export const apiUrl: string | undefined = env.VITE_ILAD_API_URL?.trim().replace(/\/+$/, '');
const firebaseConfig = {
  apiKey: env.VITE_FIREBASE_API_KEY?.trim(),
  authDomain: env.VITE_FIREBASE_AUTH_DOMAIN?.trim() || (projectId ? `${projectId}.firebaseapp.com` : undefined),
  projectId,
  appId: env.VITE_FIREBASE_APP_ID?.trim(),
};

const requiredConfig = {
  VITE_ILAD_API_URL: apiUrl,
  VITE_FIREBASE_PROJECT_ID: projectId,
  VITE_FIREBASE_API_KEY: firebaseConfig.apiKey,
  ...(useEmulator ? {} : { VITE_FIREBASE_APP_ID: firebaseConfig.appId }),
};

export const missingConfig = Object.entries(requiredConfig)
  .filter(([, value]) => !value)
  .map(([name]) => name);

export const auth = missingConfig.length === 0
  ? getAuth(initializeApp(firebaseConfig))
  : null;

if (auth && useEmulator) {
  connectAuthEmulator(auth, 'http://127.0.0.1:9099');
}

export const persistence = auth ? setPersistence(auth, browserSessionPersistence) : Promise.resolve();
