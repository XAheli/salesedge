import axios, {
  type AxiosError,
  type AxiosInstance,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from "axios";
import type { APIResponse, PaginatedResponse } from "@/types/api/common";

const BASE_URL = import.meta.env.VITE_API_URL ?? "/api";

function createClient(): AxiosInstance {
  const instance = axios.create({
    baseURL: BASE_URL,
    timeout: 30_000,
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
  });

  instance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      const token = localStorage.getItem("salesedge_token");
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error: AxiosError) => Promise.reject(error),
  );

  instance.interceptors.response.use(
    (response) => response,
    (error: AxiosError<APIResponse<unknown>>) => {
      if (error.response?.status === 401) {
        localStorage.removeItem("salesedge_token");
        if (window.location.pathname !== "/login") {
          window.location.href = "/login";
        }
      }

      const apiError = error.response?.data?.error;
      if (apiError) {
        return Promise.reject(
          new ApiError(apiError.message, apiError.code, error.response?.status ?? 500, apiError.details),
        );
      }

      return Promise.reject(
        new ApiError(
          error.message || "An unexpected error occurred",
          "NETWORK_ERROR",
          error.response?.status ?? 0,
        ),
      );
    },
  );

  return instance;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly status: number,
    public readonly details?: Record<string, unknown> | null,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export const apiClient = createClient();

export async function get<T>(url: string, config?: AxiosRequestConfig): Promise<APIResponse<T>> {
  const response = await apiClient.get<APIResponse<T>>(url, config);
  return response.data;
}

export async function getPaginated<T>(
  url: string,
  config?: AxiosRequestConfig,
): Promise<PaginatedResponse<T>> {
  const response = await apiClient.get<PaginatedResponse<T>>(url, config);
  return response.data;
}

export async function post<T>(
  url: string,
  data?: unknown,
  config?: AxiosRequestConfig,
): Promise<APIResponse<T>> {
  const response = await apiClient.post<APIResponse<T>>(url, data, config);
  return response.data;
}

export async function put<T>(
  url: string,
  data?: unknown,
  config?: AxiosRequestConfig,
): Promise<APIResponse<T>> {
  const response = await apiClient.put<APIResponse<T>>(url, data, config);
  return response.data;
}

export async function del<T>(url: string, config?: AxiosRequestConfig): Promise<APIResponse<T>> {
  const response = await apiClient.delete<APIResponse<T>>(url, config);
  return response.data;
}
