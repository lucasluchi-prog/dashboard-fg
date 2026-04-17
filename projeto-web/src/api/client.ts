import axios, { AxiosError } from "axios";

export const apiClient = axios.create({
  baseURL: "/",
  withCredentials: true,
  timeout: 30_000,
});

apiClient.interceptors.response.use(
  (r) => r,
  (err: AxiosError) => {
    if (err.response?.status === 401 && window.location.pathname !== "/login") {
      window.location.href = "/login";
    }
    return Promise.reject(err);
  },
);
