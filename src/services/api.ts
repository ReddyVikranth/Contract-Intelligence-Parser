const API_BASE_URL = 'http://localhost:8000/api';

export interface ContractUploadResponse {
  contract_id: string;
  message: string;
  status: string;
}

export interface ContractStatusResponse {
  contract_id: string;
  status: string;
  progress_percentage: number;
  error_message?: string;
}

export interface ContractListResponse {
  contracts: any[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export const uploadContract = async (file: File): Promise<ContractUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/contracts/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Upload failed');
  }

  return response.json();
};

export const getContractStatus = async (contractId: string): Promise<ContractStatusResponse> => {
  const response = await fetch(`${API_BASE_URL}/contracts/${contractId}/status`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get status');
  }

  return response.json();
};

export const getContract = async (contractId: string) => {
  const response = await fetch(`${API_BASE_URL}/contracts/${contractId}`);

  if (!response.ok) {
    const error = await response.json();
    throw { response: { status: response.status }, message: error.detail || 'Failed to get contract' };
  }

  return response.json();
};

export const getContracts = async (
  page: number = 1,
  pageSize: number = 10,
  status?: string
): Promise<ContractListResponse> => {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
  });

  if (status) {
    params.append('status', status);
  }

  const response = await fetch(`${API_BASE_URL}/contracts?${params}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get contracts');
  }

  return response.json();
};

export const downloadContract = async (contractId: string, filename: string) => {
  const response = await fetch(`${API_BASE_URL}/contracts/${contractId}/download`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Download failed');
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.style.display = 'none';
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
};