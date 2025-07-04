import React from 'react';
import { ShieldCheckIcon, AlertCircleIcon, AlertTriangleIcon, InfoIcon, CheckCircleIcon } from 'lucide-react';

interface ComplianceIssue {
  id: number;
  title: string;
  status: string;
  description: string;
  suggestion: string;
  regulation: string;
  section: string;
}

interface ComplianceTabProps {
  issuesData: any;
  loading: boolean;
  error: string;
}

const ComplianceTab: React.FC<ComplianceTabProps> = ({ issuesData, loading, error }) => {
  console.log('Rendering ComplianceTab with issuesData:', issuesData);
  const issues: ComplianceIssue[] = issuesData?.issues || [];
  const summary = {
    total_requirements: issuesData?.total_requirements || 0,
    compliant_count: issuesData?.compliant_count || 0,
    non_compliant_count: issuesData?.non_compliant_count || 0
  };

  const [hoveredItem, setHoveredItem] = React.useState<number | null>(null);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'warning':
        return <AlertTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'error':
        return <AlertCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <InfoIcon className="h-5 w-5 text-blue-500" />;
    }
  };

  const getStatusClass = (status: string) => {
    switch (status) {
      case 'success':
        return 'border-green-800 bg-green-900/20';
      case 'warning':
        return 'border-yellow-800 bg-yellow-900/20';
      case 'error':
        return 'border-red-800 bg-red-900/20';
      default:
        return 'border-gray-700 bg-gray-800';
    }
  };

  if (loading) {
    return (
      <div>
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-white flex items-center">
            <ShieldCheckIcon className="mr-3 h-8 w-8 text-blue-400" />
            Compliance
          </h1>
          <p className="text-gray-400 mt-2">
            Regulatory compliance issues and AI-generated suggestions
          </p>
        </header>
        <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-gray-800 rounded-xl p-4 flex items-center">
              <div className="rounded-full bg-gray-700 p-3 mr-4">
                <div className="h-6 w-6 bg-gray-600 rounded"></div>
              </div>
              <div>
                <div className="h-3 bg-gray-600 rounded w-20 mb-1"></div>
                <div className="h-6 bg-gray-600 rounded w-12"></div>
              </div>
            </div>
          ))}
        </div>
        <div className="animate-pulse space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="border border-gray-700 rounded-lg p-4">
              <div className="flex items-start">
                <div className="mr-3">
                  <div className="h-5 w-5 bg-gray-600 rounded"></div>
                </div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-600 rounded mb-2"></div>
                  <div className="h-3 bg-gray-600 rounded w-3/4"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-white flex items-center">
            <ShieldCheckIcon className="mr-3 h-8 w-8 text-blue-400" />
            Compliance
          </h1>
          <p className="text-gray-400 mt-2">
            Regulatory compliance issues and AI-generated suggestions
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
          <ShieldCheckIcon className="mr-3 h-8 w-8 text-blue-400" />
          Compliance
        </h1>
        <p className="text-gray-400 mt-2">
          Regulatory compliance issues and AI-generated suggestions
        </p>
      </header>
      <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-800 rounded-xl p-4 flex items-center">
          <div className="rounded-full bg-blue-900/30 p-3 mr-4">
            <ShieldCheckIcon className="h-6 w-6 text-blue-400" />
          </div>
          <div>
            <p className="text-sm text-gray-400">Total Requirements</p>
            <p className="text-2xl font-bold">{summary.total_requirements}</p>
          </div>
        </div>
        <div className="bg-gray-800 rounded-xl p-4 flex items-center">
          <div className="rounded-full bg-green-900/30 p-3 mr-4">
            <CheckCircleIcon className="h-6 w-6 text-green-400" />
          </div>
          <div>
            <p className="text-sm text-gray-400">Compliant</p>
            <p className="text-2xl font-bold text-green-400">{summary.compliant_count}</p>
          </div>
        </div>
        <div className="bg-gray-800 rounded-xl p-4 flex items-center">
          <div className="rounded-full bg-red-900/30 p-3 mr-4">
            <AlertCircleIcon className="h-6 w-6 text-red-400" />
          </div>
          <div>
            <p className="text-sm text-gray-400">Non-Compliant</p>
            <p className="text-2xl font-bold text-red-400">{summary.non_compliant_count}</p>
          </div>
        </div>
      </div>
      {issues.length === 0 ? (
        <div className="text-gray-400 text-center py-8">
          No compliance issues found. Run compliance analysis to identify potential issues.
        </div>
      ) : (
        <div className="space-y-4">
          {issues.map(issue => (
            <div 
              key={issue.id} 
              className={`border rounded-lg p-4 relative ${getStatusClass(issue.status)}`} 
              onMouseEnter={() => setHoveredItem(issue.id)} 
              onMouseLeave={() => setHoveredItem(null)}
            >
              <div className="flex items-start">
                <div className="mr-3">{getStatusIcon(issue.status)}</div>
                <div>
                  <div className="flex items-center">
                    <h3 className="font-medium text-white">{issue.title}</h3>
                    <span className="ml-3 px-2 py-0.5 text-xs rounded-full bg-gray-700 text-gray-300">
                      {issue.regulation} {issue.section}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 mt-1">{issue.description}</p>
                  {hoveredItem === issue.id && (
                    <div className="mt-3 p-3 bg-gray-900 rounded-lg border border-gray-700">
                      <div className="mb-2">
                        <span className="text-xs text-gray-400 block">Suggestion</span>
                        <span className="text-sm">{issue.suggestion}</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ComplianceTab;