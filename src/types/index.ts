// Component Props Types
export interface PageProps {
  params: Record<string, string | string[]>;
  searchParams: Record<string, string | string[]>;
}

// Common API Response Type
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
