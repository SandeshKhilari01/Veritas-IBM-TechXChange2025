import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, X, CheckCircle, AlertCircle, Play, Settings, BarChart3 } from 'lucide-react';
import { uploadFiles, processFiles, setupIngestion, analyzeRegulation } from '../api';

interface UploadedFile {
  name: string;
  size: string;
  status: 'uploading' | 'uploaded' | 'processing' | 'processed' | 'error';
  progress?: number;
  error?: string;
}

interface WorkflowStep {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  error?: string;
}

interface DocumentUploadProps {
  onAnalysisComplete?: () => void;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ onAnalysisComplete }) => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [companyDescription, setCompanyDescription] = useState('');
  const [workflowSteps, setWorkflowSteps] = useState<WorkflowStep[]>([
    { id: 'ingestion', name: 'Setup Ingestion', status: 'pending' },
    { id: 'processing', name: 'Process Files', status: 'pending' },
    { id: 'analysis', name: 'Analyze Compliance', status: 'pending' }
  ]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const updateWorkflowStep = (stepId: string, status: WorkflowStep['status'], error?: string) => {
    setWorkflowSteps(prev => prev.map(step => 
      step.id === stepId 
        ? { ...step, status, error }
        : step
    ));
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFiles = Array.from(e.dataTransfer.files);
    handleFileUpload(droppedFiles);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    handleFileUpload(selectedFiles);
  };

  const handleFileUpload = async (fileList: File[]) => {
    if (fileList.length === 0) return;

    setUploading(true);
    
    // Add files to state
    const newFiles: UploadedFile[] = fileList.map(file => ({
      name: file.name,
      size: formatFileSize(file.size),
      status: 'uploading'
    }));
    
    setFiles(prev => [...prev, ...newFiles]);

    try {
      const formData = new FormData();
      fileList.forEach(file => {
        formData.append('files', file);
        console.log('DEBUG: Appending file to FormData:', file.name);
      });

      const response = await uploadFiles(formData);
      
      if (response.success) {
        setFiles(prev => prev.map(file => 
          fileList.some(f => f.name === file.name) 
            ? { ...file, status: 'uploaded' as const }
            : file
        ));
      } else {
        setFiles(prev => prev.map(file => 
          fileList.some(f => f.name === file.name) 
            ? { ...file, status: 'error' as const, error: response.error }
            : file
        ));
      }
    } catch (error) {
      console.error('DEBUG: Upload error:', error);
      setFiles(prev => prev.map(file => 
        fileList.some(f => f.name === file.name) 
          ? { ...file, status: 'error' as const, error: 'Upload failed' }
          : file
      ));
    } finally {
      setUploading(false);
    }
  };

  const handleSetupIngestion = async () => {
    if (!companyDescription.trim()) return;
    
    updateWorkflowStep('ingestion', 'running');
    try {
      const response = await setupIngestion(companyDescription);
      if (response.success) {
        updateWorkflowStep('ingestion', 'completed');
      } else {
        updateWorkflowStep('ingestion', 'error', response.error);
      }
    } catch (error) {
      console.error('Setup ingestion error:', error);
      updateWorkflowStep('ingestion', 'error', 'Setup failed');
    }
  };

  const handleProcessFiles = async () => {
    const uploadedFiles = files.filter(f => f.status === 'uploaded');
    if (uploadedFiles.length === 0) return;

    updateWorkflowStep('processing', 'running');
    
    // Update file status to processing
    setFiles(prev => prev.map(file => 
      file.status === 'uploaded' 
        ? { ...file, status: 'processing' as const }
        : file
    ));

    try {
      const response = await processFiles();
      
      if (response.success) {
        updateWorkflowStep('processing', 'completed');
        // Update file status to processed
        setFiles(prev => prev.map(file => 
          file.status === 'processing' 
            ? { ...file, status: 'processed' as const }
            : file
        ));
      } else {
        updateWorkflowStep('processing', 'error', response.error);
        setFiles(prev => prev.map(file => 
          file.status === 'processing' 
            ? { ...file, status: 'error' as const, error: response.error }
            : file
        ));
      }
    } catch (error) {
      updateWorkflowStep('processing', 'error', 'Processing failed');
      setFiles(prev => prev.map(file => 
        file.status === 'processing' 
          ? { ...file, status: 'error' as const, error: 'Processing failed' }
          : file
      ));
    }
  };

  const handleAnalyzeCompliance = async () => {
    updateWorkflowStep('analysis', 'running');
    try {
      // Analyze against GDPR first
      const response = await analyzeRegulation('GDPR');
      if (response.success) {
        updateWorkflowStep('analysis', 'completed');
        if (typeof onAnalysisComplete === 'function') {
          onAnalysisComplete();
        }
      } else {
        updateWorkflowStep('analysis', 'error', response.error);
      }
    } catch (error) {
      console.error('Analysis error:', error);
      updateWorkflowStep('analysis', 'error', 'Analysis failed');
    }
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploading':
        return <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-400"></div>;
      case 'uploaded':
        return <CheckCircle className="h-4 w-4 text-green-400" />;
      case 'processing':
        return <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-400"></div>;
      case 'processed':
        return <CheckCircle className="h-4 w-4 text-green-400" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-400" />;
      default:
        return null;
    }
  };

  const getStatusText = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploading':
        return 'Uploading...';
      case 'uploaded':
        return 'Uploaded';
      case 'processing':
        return 'Processing...';
      case 'processed':
        return 'Processed';
      case 'error':
        return 'Error';
      default:
        return '';
    }
  };

  const getWorkflowStepIcon = (step: WorkflowStep) => {
    switch (step.status) {
      case 'pending':
        return <div className="w-6 h-6 rounded-full bg-gray-600 flex items-center justify-center">
          <span className="text-xs text-gray-400">{step.id === 'ingestion' ? '1' : step.id === 'processing' ? '2' : '3'}</span>
        </div>;
      case 'running':
        return <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-400"></div>;
      case 'completed':
        return <CheckCircle className="h-6 w-6 text-green-400" />;
      case 'error':
        return <AlertCircle className="h-6 w-6 text-red-400" />;
      default:
        return null;
    }
  };

  const getWorkflowStepButton = (step: WorkflowStep) => {
    const isDisabled = step.status === 'running' || 
      (step.id === 'processing' && workflowSteps.find(s => s.id === 'ingestion')?.status !== 'completed') ||
      (step.id === 'analysis' && workflowSteps.find(s => s.id === 'processing')?.status !== 'completed');

    const getButtonText = () => {
      switch (step.status) {
        case 'pending':
          return step.name;
        case 'running':
          return 'Running...';
        case 'completed':
          return 'Completed';
        case 'error':
          return 'Retry';
        default:
          return step.name;
      }
    };

    const getButtonColor = () => {
      switch (step.status) {
        case 'pending':
          return 'bg-blue-600 hover:bg-blue-700';
        case 'running':
          return 'bg-yellow-600 cursor-not-allowed';
        case 'completed':
          return 'bg-green-600 cursor-not-allowed';
        case 'error':
          return 'bg-red-600 hover:bg-red-700';
        default:
          return 'bg-blue-600 hover:bg-blue-700';
      }
    };

    const handleClick = () => {
      switch (step.id) {
        case 'ingestion':
          handleSetupIngestion();
          break;
        case 'processing':
          handleProcessFiles();
          break;
        case 'analysis':
          handleAnalyzeCompliance();
          break;
      }
    };

    return (
      <button
        onClick={handleClick}
        disabled={isDisabled}
        className={`${getButtonColor()} text-white px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50`}
      >
        {getButtonText()}
      </button>
    );
  };

  const uploadedFiles = files.filter(f => f.status === 'uploaded');
  const processedFiles = files.filter(f => f.status === 'processed');

  return (
    <div className="bg-gray-800 rounded-xl p-6 h-full">
      <h2 className="text-xl font-bold text-white mb-4">Document Upload & Processing</h2>
      
      {/* Workflow Steps */}
      <div className="mb-6 p-4 bg-gray-700 rounded-lg">
        <h3 className="text-sm font-medium text-gray-300 mb-4">Workflow Steps</h3>
        <div className="space-y-3">
          {workflowSteps.map((step) => (
            <div key={step.id} className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {getWorkflowStepIcon(step)}
                <div>
                  <p className="text-sm font-medium text-white">{step.name}</p>
                  {step.error && (
                    <p className="text-xs text-red-400">{step.error}</p>
                  )}
                </div>
              </div>
              {getWorkflowStepButton(step)}
            </div>
          ))}
        </div>
      </div>

      {/* Company Description Input */}
      <div className="mb-6 p-4 bg-gray-700 rounded-lg">
        <h3 className="text-sm font-medium text-gray-300 mb-3">Company Description</h3>
        <input
          type="text"
          value={companyDescription}
          onChange={(e) => setCompanyDescription(e.target.value)}
          placeholder="e.g., TechCorp - software company specializing in healthcare solutions"
          className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-lg text-sm text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
          disabled={workflowSteps.find(s => s.id === 'ingestion')?.status === 'completed'}
        />
      </div>
      
      <div 
        className={`border-2 border-dashed rounded-lg p-6 flex flex-col items-center justify-center transition-colors ${
          isDragging ? 'border-blue-500 bg-blue-900/20' : 'border-gray-700 hover:border-gray-500'
        }`} 
        onDragOver={handleDragOver} 
        onDragLeave={handleDragLeave} 
        onDrop={handleDrop}
      >
        <UploadCloud className="h-10 w-10 text-gray-500 mb-4" />
        <p className="text-sm text-center mb-2">
          <span className="font-medium">Click to upload</span> or drag and drop
        </p>
        <p className="text-xs text-gray-500 text-center mb-4">
          PDF, DOC, DOCX, TXT (max 50MB per file)
        </p>
        <button 
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
        >
          {uploading ? 'Uploading...' : 'Select Files'}
        </button>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.txt"
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {files.length > 0 && (
        <div className="mt-4">
          <h3 className="text-sm font-medium text-gray-400 mb-2">
            Uploaded Documents
          </h3>
          <div className="space-y-2">
            {files.map((file, index) => (
              <div key={index} className="flex items-center justify-between bg-gray-700 rounded-lg p-3">
                <div className="flex items-center">
                  <FileText className="h-5 w-5 text-blue-400 mr-3" />
                  <div>
                    <p className="text-sm font-medium">{file.name}</p>
                    <p className="text-xs text-gray-400">{file.size}</p>
                    {file.error && (
                      <p className="text-xs text-red-400">{file.error}</p>
                    )}
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-400">
                    {getStatusText(file.status)}
                  </span>
                  {getStatusIcon(file.status)}
                  <button 
                    className="text-gray-400 hover:text-gray-200" 
                    onClick={() => removeFile(index)}
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {processedFiles.length > 0 && (
        <div className="mt-4 p-3 bg-green-900/20 border border-green-800 rounded-lg">
          <p className="text-sm text-green-400">
            ✓ {processedFiles.length} file{processedFiles.length > 1 ? 's' : ''} processed successfully
          </p>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;