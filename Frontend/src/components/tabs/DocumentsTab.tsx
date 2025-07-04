import React from 'react';
import { FileTextIcon, SearchIcon, FilterIcon, CheckCircleIcon, XCircleIcon, AlertTriangleIcon } from 'lucide-react';

interface Document {
  id: number;
  name: string;
  uploadDate: string;
  size: string;
  status: 'processed' | 'processing' | 'failed' | 'uploaded';
  issues: number | null;
}

interface DocumentsTabProps {
  uploadedFilesData: any;
  loading: boolean;
  error: string;
}

const DocumentsTab: React.FC<DocumentsTabProps> = ({ uploadedFilesData, loading, error }) => {
  console.log('Rendering DocumentsTab with uploadedFilesData:', uploadedFilesData);
  const [searchTerm, setSearchTerm] = React.useState('');
  const [filterStatus, setFilterStatus] = React.useState<string>('all');
  const documents: Document[] = (uploadedFilesData?.files || []).map((doc: any) => ({
    ...doc,
    uploadDate: doc.upload_date,
  }));
  console.log('Documents array:', documents);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  const getStatusIcon = (status: string, issues: number | null) => {
    if (status === 'processing') {
      return (
        <span className="inline-flex items-center px-2 py-1 text-xs rounded-full bg-blue-900/30 text-blue-400 border border-blue-800">
          Processing
        </span>
      );
    } else if (status === 'failed') {
      return (
        <span className="inline-flex items-center px-2 py-1 text-xs rounded-full bg-red-900/30 text-red-400 border border-red-800">
          <XCircleIcon className="h-3 w-3 mr-1" />
          Failed
        </span>
      );
    } else if (status === 'uploaded') {
      return (
        <span className="inline-flex items-center px-2 py-1 text-xs rounded-full bg-yellow-900/30 text-yellow-400 border border-yellow-800">
          Uploaded
        </span>
      );
    } else if (issues && issues > 0) {
      return (
        <span className="inline-flex items-center px-2 py-1 text-xs rounded-full bg-yellow-900/30 text-yellow-400 border border-yellow-800">
          <AlertTriangleIcon className="h-3 w-3 mr-1" />
          {issues} issues
        </span>
      );
    } else {
      return (
        <span className="inline-flex items-center px-2 py-1 text-xs rounded-full bg-green-900/30 text-green-400 border border-green-800">
          <CheckCircleIcon className="h-3 w-3 mr-1" />
          Compliant
        </span>
      );
    }
  };

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || doc.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return (
      <div>
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-white flex items-center">
            <FileTextIcon className="mr-3 h-8 w-8 text-blue-400" />
            Documents
          </h1>
          <p className="text-gray-400 mt-2">
            Upload history and document scan results
          </p>
        </header>
        <div className="mb-6 flex justify-between items-center">
          <div className="relative w-64">
            <div className="w-full bg-gray-700 border border-gray-600 rounded-lg py-2 pl-10 pr-4 h-9"></div>
          </div>
          <div className="flex space-x-3">
            <div className="w-20 h-9 bg-gray-700 rounded-lg"></div>
            <div className="w-24 h-9 bg-gray-700 rounded-lg"></div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-xl overflow-hidden">
          <div className="animate-pulse">
            {[1, 2, 3].map((i) => (
              <div key={i} className="p-6 border-b border-gray-700">
                <div className="flex items-center">
                  <div className="h-5 w-5 bg-gray-600 rounded mr-3"></div>
                  <div className="flex-1">
                    <div className="h-4 bg-gray-600 rounded w-1/3 mb-2"></div>
                    <div className="h-3 bg-gray-600 rounded w-1/4"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-white flex items-center">
            <FileTextIcon className="mr-3 h-8 w-8 text-blue-400" />
            Documents
          </h1>
          <p className="text-gray-400 mt-2">
            Upload history and document scan results
          </p>
        </header>
        <div className="text-red-400 text-center py-8">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div>
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center">
          <FileTextIcon className="mr-3 h-8 w-8 text-blue-400" />
          Documents
        </h1>
        <p className="text-gray-400 mt-2">
          Upload history and document scan results
        </p>
      </header>
      <div className="mb-6 flex justify-between items-center">
        <div className="relative w-64">
          <input 
            type="text" 
            placeholder="Search documents..." 
            className="w-full bg-gray-700 border border-gray-600 rounded-lg py-2 pl-10 pr-4 text-sm text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <SearchIcon className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
        </div>
        <div className="flex space-x-3">
          <select 
            className="flex items-center px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="all">All Status</option>
            <option value="uploaded">Uploaded</option>
            <option value="processed">Processed</option>
            <option value="processing">Processing</option>
            <option value="failed">Failed</option>
          </select>
          <button className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm">
            Upload New
          </button>
        </div>
      </div>
      <div className="bg-gray-800 rounded-xl overflow-hidden">
        {documents.length === 0 ? (
          <div className="text-center py-12">
            <FileTextIcon className="h-12 w-12 text-gray-500 mx-auto mb-4" />
            <p className="text-gray-400">No documents uploaded yet</p>
            <p className="text-sm text-gray-500 mt-2">Upload documents to start compliance analysis</p>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-700">
            <thead>
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Document</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Upload Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Size</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="bg-gray-800 divide-y divide-gray-700">
              {filteredDocuments.map((doc) => (
                <tr key={doc.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-white">{doc.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">{formatDate(doc.uploadDate)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">{doc.size}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{getStatusIcon(doc.status, doc.issues)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default DocumentsTab;