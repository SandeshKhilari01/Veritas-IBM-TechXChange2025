import React, { useState, useEffect } from 'react';
import { CheckCircleIcon } from 'lucide-react';
import { getProjectOverview } from '../api';

interface ProjectData {
  project_name: string;
  project_id: string;
  analysis_date: string;
  scanned_by: string;
  documents_evaluated: string;
  compliance_status: string;
  key_regulations: string[];
}

const ProjectOverview = () => {
  const [data, setData] = useState<ProjectData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await getProjectOverview();
        if (response.success) {
          setData(response.overview);
        } else {
          setError(response.error || 'Failed to fetch project data');
        }
      } catch (err) {
        setError('Failed to connect to the server');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'compliant':
        return 'bg-green-400';
      case 'partial':
        return 'bg-yellow-400';
      case 'non-compliant':
        return 'bg-red-400';
      default:
        return 'bg-gray-400';
    }
  };

  const getStatusTextColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'compliant':
        return 'text-green-400';
      case 'partial':
        return 'text-yellow-400';
      case 'non-compliant':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-xl p-6 h-full">
        <h2 className="text-xl font-bold text-white mb-4 flex items-center">
          Project Overview
          <CheckCircleIcon className="ml-2 h-5 w-5 text-green-400" />
        </h2>
        <div className="animate-pulse space-y-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i}>
              <div className="h-3 bg-gray-600 rounded w-1/3 mb-1"></div>
              <div className="h-4 bg-gray-600 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-800 rounded-xl p-6 h-full">
        <h2 className="text-xl font-bold text-white mb-4 flex items-center">
          Project Overview
          <CheckCircleIcon className="ml-2 h-5 w-5 text-green-400" />
        </h2>
        <div className="text-red-400 text-center py-8">
          {error}
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-gray-800 rounded-xl p-6 h-full">
        <h2 className="text-xl font-bold text-white mb-4 flex items-center">
          Project Overview
          <CheckCircleIcon className="ml-2 h-5 w-5 text-green-400" />
        </h2>
        <div className="text-gray-400 text-center py-8">
          No project data available. Please setup ingestion first.
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-xl p-6 h-full">
      <h2 className="text-xl font-bold text-white mb-4 flex items-center">
        Project Overview
        <CheckCircleIcon className="ml-2 h-5 w-5 text-green-400" />
      </h2>
      <div className="space-y-4">
        <div>
          <p className="text-sm text-gray-400">Project Name & ID</p>
          <p className="font-medium">{data.project_name} ({data.project_id})</p>
        </div>
        <div>
          <p className="text-sm text-gray-400">Date of Analysis</p>
          <p className="font-medium">{data.analysis_date}</p>
        </div>
        <div>
          <p className="text-sm text-gray-400">Scanned By</p>
          <p className="font-medium">{data.scanned_by}</p>
        </div>
        <div>
          <p className="text-sm text-gray-400">Documents Evaluated</p>
          <p className="font-medium">
            {data.documents_evaluated || 'No documents processed'}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-400">Compliance Status</p>
          <div className="flex items-center mt-1">
            <div className={`w-3 h-3 rounded-full ${getStatusColor(data.compliance_status)} mr-2`}></div>
            <span className={`font-medium ${getStatusTextColor(data.compliance_status)}`}>
              {data.compliance_status}
            </span>
          </div>
        </div>
        <div className="pt-2">
          <p className="text-sm text-gray-400">Key Regulations</p>
          <div className="flex flex-wrap gap-2 mt-1">
            {data.key_regulations && data.key_regulations.length > 0 ? (
              data.key_regulations.map((regulation, index) => (
                <span key={index} className="px-2 py-1 bg-gray-700 rounded-md text-xs">
                  {regulation}
                </span>
              ))
            ) : (
              <span className="text-gray-500 text-xs">No regulations analyzed yet</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectOverview;