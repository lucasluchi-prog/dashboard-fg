import axios, { AxiosError } from "axios";

// Em prod, frontend (.web.app) fala direto com Cloud Run (.run.app) via CORS.
// Em dev, o proxy do Vite (localhost:5173 -> 8080) faz o papel — VITE_API_BASE vazio = baseURL '/'.
const API_BASE = import.meta.env.VITE_API_BASE || "";

export const apiClient = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
  timeout: 30_000,
});

export function goToLogin(): void {
  window.location.href = `${API_BASE}/login`;
}

apiClient.interceptors.response.use(
  (r) => r,
  (err: AxiosError) => {
    if (
      err.response?.status === 401 &&
      window.location.pathname !== "/login" &&
      !window.location.pathname.includes("/login")
    ) {
      goToLogin();
    }
    return Promise.reject(err);
  },
);
