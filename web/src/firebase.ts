import { initializeApp } from '@firebase/app';
import { browserSessionPersistence, connectAuthEmulator, getAuth, setPersistence } from '@firebase/auth';

const env = import.meta.env;
const useEmulator = env.DEV && env.VITE_USE_FIREBASE_EMULATOR === 'true';

export const apiUrl: string | undefined = env.VITE_ILAD_API_URL?.replace(/\/+$/, '');
const firebaseConfig = {
  apiKey: env.VITE_FIREBASE_API_KEY,
  authDomain: env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: env.VITE_FIREBASE_PROJECT_ID,
  appId: env.VITE_FIREBASE_APP_ID,
};

export const auth = apiUrl && firebaseConfig.apiKey && firebaseConfig.projectId &&
  (useEmulator || (firebaseConfig.appId && firebaseConfig.authDomain))
  ? getAuth(initializeApp(firebaseConfig))
  : null;

if (auth && useEmulator) {
  connectAuthEmulator(auth, 'http://127.0.0.1:9099');
}

export const persistence = auth ? setPersistence(auth, browserSessionPersistence) : Promise.resolve();
