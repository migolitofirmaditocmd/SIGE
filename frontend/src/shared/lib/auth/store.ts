/**
 * Almacén en memoria de autenticación y sesión (RN-SEG-01).
 * Los tokens JWT sensibles residen únicamente en memoria y no en localStorage.
 */

export interface AuthUser {
  id: string;
  username: string;
  email: string;
  role: "ADMIN" | "PREFECTO" | "DOCENTE" | "PAD";
  fullName: string;
}

export interface AuthState {
  user: AuthUser | null;
  accessToken: string | null;
  isAuthenticated: boolean;
}

let currentAuthState: AuthState = {
  user: null,
  accessToken: null,
  isAuthenticated: false,
};

export function getAuthState(): AuthState {
  return currentAuthState;
}

export function setAuthState(newState: Partial<AuthState>): void {
  currentAuthState = { ...currentAuthState, ...newState };
}

export function clearAuthState(): void {
  currentAuthState = {
    user: null,
    accessToken: null,
    isAuthenticated: false,
  };
}

