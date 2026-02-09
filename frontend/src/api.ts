import axios from 'axios';

// 使用相对路径，让请求通过当前页面的协议和域名
const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 300000,  // 5分钟超时
});

export interface Detection {
  type: string;
  original: string;
  start: number;
  end: number;
}

export interface MaskResponse {
  masked_text: string;
  detections: Detection[];
}

export async function uploadDocument(file: File): Promise<string> {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post<{ text: string }>('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data.text;
}

export async function maskPII(text: string, categories: string[]): Promise<MaskResponse> {
  const response = await api.post<MaskResponse>('/mask', { text, categories });
  return response.data;
}

export async function healthCheck(): Promise<boolean> {
  try {
    await api.get('/health');
    return true;
  } catch {
    return false;
  }
}
