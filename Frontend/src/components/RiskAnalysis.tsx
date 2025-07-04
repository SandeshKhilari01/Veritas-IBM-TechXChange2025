import React, { useState, useEffect } from 'react';
import { AlertCircleIcon, AlertTriangleIcon, InfoIcon } from 'lucide-react';
import { getRiskAnalysis } from '../api';

interface Risk {
  id: number;
  title: string;
  description: string;
  severity: string;
  regulation: string;
  recommendation: string;
}

const RiskAnalysis = () => {
  const [selectedRisk, setSelectedRisk] = useState<number | null>(null);
  const [risks, setRisks] = useState<Risk[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalIssues, setTotalIssues] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await getRiskAnalysis();
        if (response.success) {
          setRisks(response.risks || []);
          setTotalIssues(response.total_issues || 0);
        } else {
          setError(response.error || 'Failed to fetch risk data');
        }
      } catch (err) {
        setError('Failed to connect to the server');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <AlertCircleIcon className="h-5 w-5 text-red-500" />;
      case 'high':
        return <AlertTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'medium':
        return <AlertTriangleIcon className="h-5 w-5 text-blue-500" />;
      default:
        return <InfoIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getSeverityClass = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-900/20 text-red-400 border-red-800';
      case 'high':
        return 'bg-yellow-900/20 text-yellow-400 border-yellow-800';
      case 'medium':
        return 'bg-blue-900/20 text-blue-400 border-blue-800';
      default:
        return 'bg-gray-700/50 text-gray-400 border-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-xl p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-white">Risk Analysis</h2>
          <div className="text-sm text-gray-400">
            <span className="font-medium text-white">-</span> total issues
          </div>
        </div>
        <div className="animate-pulse space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="p-4 border border-gray-700 rounded-lg">
              <div className="flex items-start">
                <div className="mr-3 mt-0.5">
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
      <div className="bg-gray-800 rounded-xl p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-white">Risk Analysis</h2>
        </div>
        <div className="text-red-400 text-center py-8">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-xl p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-white">Risk Analysis</h2>
        <div className="text-sm text-gray-400">
          <span className="font-medium text-white">{totalIssues}</span> total issues
        </div>
      </div>
      {risks.length === 0 ? (
        <div className="text-gray-400 text-center py-8">
          No risk issues found. Run compliance analysis to identify potential risks.
        </div>
      ) : (
        <div className="space-y-3">
          {risks.map(risk => (
            <div 
              key={risk.id} 
              className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                selectedRisk === risk.id 
                  ? getSeverityClass(risk.severity) 
                  : 'border-gray-700 hover:border-gray-600'
              }`} 
              onClick={() => setSelectedRisk(selectedRisk === risk.id ? null : risk.id)}
            >
              <div className="flex items-start">
                <div className="mr-3 mt-0.5">
                  {getSeverityIcon(risk.severity)}
                </div>
                <div className="flex-1">
                  <div className="flex justify-between">
                    <h3 className="font-medium">{risk.title}</h3>
                    <span className={`text-xs px-2 py-1 rounded-full uppercase font-bold ${
                      risk.severity === 'critical' 
                        ? 'bg-red-900/50 text-red-400' 
                        : risk.severity === 'high' 
                        ? 'bg-yellow-900/50 text-yellow-400' 
                        : 'bg-blue-900/50 text-blue-400'
                    }`}>
                      {risk.severity}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 mt-1">{risk.description}</p>
                  {selectedRisk === risk.id && (
                    <div className="mt-4 pt-4 border-t border-gray-700">
                      <div className="mb-3">
                        <span className="text-xs text-gray-400 block">
                          Regulation Reference
                        </span>
                        <span className="text-sm">{risk.regulation}</span>
                      </div>
                      <div>
                        <span className="text-xs text-gray-400 block">
                          Recommendation
                        </span>
                        <span className="text-sm">{risk.recommendation}</span>
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

export default RiskAnalysis;