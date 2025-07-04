import axios from 'axios';

const API_BASE = 'http://localhost:5000'; // Change if backend runs elsewhere

export const getStatus = async () => {
  const res = await axios.get(`${API_BASE}/status`);
  console.log('API getStatus:', res.data);
  return res.data;
};

export const uploadFiles = async (formData: FormData) => {
  const res = await axios.post(`${API_BASE}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  console.log('API uploadFiles:', res.data);
  return res.data;
};

export const setupIngestion = async (company_description: string) => {
  const res = await axios.post(`${API_BASE}/setup_ingestion`, { company_description });
  console.log('API setupIngestion:', res.data);
  return res.data;
};

export const processFiles = async () => {
  const res = await axios.post(`${API_BASE}/process_files`);
  console.log('API processFiles:', res.data);
  return res.data;
};

export const analyzeRegulation = async (regulation: string) => {
  const res = await axios.post(`${API_BASE}/analyze/${regulation}`);
  console.log('API analyzeRegulation:', res.data);
  return res.data;
};

export const generateReport = async () => {
  const res = await axios.post(`${API_BASE}/generate_report`);
  console.log('API generateReport:', res.data);
  return res.data;
};

// New API functions for dashboard data
export const getComplianceSummary = async () => {
  const res = await axios.get(`${API_BASE}/compliance_summary`);
  console.log('API getComplianceSummary:', res.data);
  return res.data;
};

export const getRiskAnalysis = async () => {
  const res = await axios.get(`${API_BASE}/risk_analysis`);
  console.log('API getRiskAnalysis:', res.data);
  return res.data;
};

export const getProjectOverview = async () => {
  const res = await axios.get(`${API_BASE}/project_overview`);
  console.log('API getProjectOverview:', res.data);
  return res.data;
};

export const getComplianceIssues = async () => {
  const res = await axios.get(`${API_BASE}/compliance_issues`);
  console.log('API getComplianceIssues:', res.data);
  return res.data;
};

export const resetSession = async () => {
  const res = await axios.post(`${API_BASE}/reset`);
  console.log('API resetSession:', res.data);
  return res.data;
};

export const getUploadedFiles = async () => {
  const res = await axios.get(`${API_BASE}/uploaded_files`);
  console.log('API getUploadedFiles:', res.data);
  return res.data;
}; 