import React from 'react';
import { AlertTriangleIcon, AlertCircleIcon, InfoIcon, XCircleIcon, ArrowUpIcon, ArrowDownIcon } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip, Cell } from 'recharts';

interface Risk {
  id: number;
  title: string;
  description: string;
  severity: string;
  priority: string;
  regulation: string;
  section: string;
  impact: string;
  suggestion: string;
}

interface RiskTabProps {
  riskData: any;
  loading: boolean;
  error: string;
}

const RiskTab: React.FC<RiskTabProps> = ({ riskData, loading, error }) => {
  const risks: Risk[] = (riskData?.risks || []).map((risk: any, index: number) => ({
    id: risk.id || index + 1,
    title: risk.title,
    description: risk.description,
    severity: risk.severity || 'medium',
    priority: risk.severity === 'critical' || risk.severity === 'high' ? 'high' : 'medium',
    regulation: risk.regulation,
    section: risk.regulation?.split(' ').pop() || '',
    impact: 'Potential compliance violation and security risk',
    suggestion: risk.recommendation
  }));

  const [selectedRisk, setSelectedRisk] = React.useState<Risk | null>(null);
  const [showModal, setShowModal] = React.useState(false);

  const risksByCategory = {
    critical: risks.filter(risk => risk.severity === 'critical').length,
    high: risks.filter(risk => risk.severity === 'high').length,
    medium: risks.filter(risk => risk.severity === 'medium').length,
    low: risks.filter(risk => risk.severity === 'low').length
  };

  const chartData = [
    {
      name: 'Critical',
      value: risksByCategory.critical,
      color: '#EF4444'
    },
    {
      name: 'High',
      value: risksByCategory.high,
      color: '#F59E0B'
    },
    {
      name: 'Medium',
      value: risksByCategory.medium,
      color: '#3B82F6'
    },
    {
      name: 'Low',
      value: risksByCategory.low,
      color: '#10B981'
    }
  ];

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <AlertCircleIcon className="h-5 w-5 text-red-500" />;
      case 'high':
        return <AlertTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'medium':
        return <AlertTriangleIcon className="h-5 w-5 text-blue-500" />;
      default:
        return <InfoIcon className="h-5 w-5 text-green-500" />;
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
        return 'bg-green-900/20 text-green-400 border-green-800';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return <ArrowUpIcon className="h-4 w-4 text-red-500" />;
      case 'medium':
        return <ArrowUpIcon className="h-4 w-4 rotate-45 text-yellow-500" />;
      default:
        return <ArrowDownIcon className="h-4 w-4 text-blue-500" />;
    }
  };

  const viewRiskDetails = (risk: Risk) => {
    setSelectedRisk(risk);
    setShowModal(true);
  };

  if (loading) {
    return (
      <div>
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-white flex items-center">
            <AlertTriangleIcon className="mr-3 h-8 w-8 text-yellow-500" />
            Risk Analysis
          </h1>
          <p className="text-gray-400 mt-2">
            Identified risks and AI-generated mitigation suggestions
          </p>
        </header>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2 bg-gray-800 rounded-xl p-6">
            <div className="animate-pulse">
              <div className="h-6 bg-gray-600 rounded w-1/3 mb-4"></div>
              <div className="h-64 bg-gray-700 rounded"></div>
            </div>
          </div>
          <div className="bg-gray-800 rounded-xl p-6">
            <div className="animate-pulse">
              <div className="h-6 bg-gray-600 rounded w-1/2 mb-4"></div>
              <div className="space-y-4">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="h-12 bg-gray-700 rounded"></div>
                ))}
              </div>
            </div>
          </div>
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
            <AlertTriangleIcon className="mr-3 h-8 w-8 text-yellow-500" />
            Risk Analysis
          </h1>
          <p className="text-gray-400 mt-2">
            Identified risks and AI-generated mitigation suggestions
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
          <AlertTriangleIcon className="mr-3 h-8 w-8 text-yellow-500" />
          Risk Analysis
        </h1>
        <p className="text-gray-400 mt-2">
          Identified risks and AI-generated mitigation suggestions
        </p>
      </header>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2 bg-gray-800 rounded-xl p-6">
          <h2 className="text-xl font-bold text-white mb-4">
            Risk Distribution
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart 
                data={chartData} 
                margin={{
                  top: 5,
                  right: 30,
                  left: 0,
                  bottom: 5
                }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#1F2937',
                    borderColor: '#4B5563',
                    borderRadius: '0.375rem'
                  }} 
                  labelStyle={{
                    color: '#F9FAFB'
                  }} 
                />
                <Bar dataKey="value">
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="bg-gray-800 rounded-xl p-6">
          <h2 className="text-xl font-bold text-white mb-4">Risk Summary</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-red-900/20 border border-red-800 rounded-lg">
              <div className="flex items-center">
                <AlertCircleIcon className="h-5 w-5 text-red-500 mr-2" />
                <span>Critical</span>
              </div>
              <span className="text-xl font-bold">
                {risksByCategory.critical}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-yellow-900/20 border border-yellow-800 rounded-lg">
              <div className="flex items-center">
                <AlertTriangleIcon className="h-5 w-5 text-yellow-500 mr-2" />
                <span>High</span>
              </div>
              <span className="text-xl font-bold">{risksByCategory.high}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-blue-900/20 border border-blue-800 rounded-lg">
              <div className="flex items-center">
                <AlertTriangleIcon className="h-5 w-5 text-blue-500 mr-2" />
                <span>Medium</span>
              </div>
              <span className="text-xl font-bold">{risksByCategory.medium}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-green-900/20 border border-green-800 rounded-lg">
              <div className="flex items-center">
                <InfoIcon className="h-5 w-5 text-green-500 mr-2" />
                <span>Low</span>
              </div>
              <span className="text-xl font-bold">{risksByCategory.low}</span>
            </div>
          </div>
        </div>
      </div>

      {risks.length === 0 ? (
        <div className="text-center py-12">
          <AlertTriangleIcon className="h-12 w-12 text-gray-500 mx-auto mb-4" />
          <p className="text-gray-400">No risks identified yet</p>
          <p className="text-sm text-gray-500 mt-2">Run compliance analysis to identify potential risks</p>
        </div>
      ) : (
        <div className="space-y-4">
          {risks.map(risk => (
            <div 
              key={risk.id} 
              className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                selectedRisk?.id === risk.id 
                  ? getSeverityClass(risk.severity) 
                  : 'border-gray-700 hover:border-gray-600'
              }`} 
              onClick={() => viewRiskDetails(risk)}
            >
              <div className="flex items-start">
                <div className="mr-3">{getSeverityIcon(risk.severity)}</div>
                <div className="flex-1">
                  <div className="flex justify-between items-start">
                    <h3 className="font-medium text-white">{risk.title}</h3>
                    <div className="flex items-center space-x-2">
                      {getPriorityIcon(risk.priority)}
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
                  </div>
                  <p className="text-gray-400 text-sm mt-1">{risk.description}</p>
                  <div className="flex items-center mt-2 space-x-4 text-xs text-gray-500">
                    <span>{risk.regulation}</span>
                    <span>Impact: {risk.impact}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Risk Details Modal */}
      {showModal && selectedRisk && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-xl p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-xl font-bold text-white">{selectedRisk.title}</h2>
              <button 
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-gray-200"
              >
                <XCircleIcon className="h-6 w-6" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-medium text-gray-400 mb-1">Description</h3>
                <p className="text-white">{selectedRisk.description}</p>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-400 mb-1">Impact</h3>
                <p className="text-white">{selectedRisk.impact}</p>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-400 mb-1">Regulation</h3>
                <p className="text-white">{selectedRisk.regulation}</p>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-400 mb-1">Mitigation Suggestion</h3>
                <p className="text-white">{selectedRisk.suggestion}</p>
              </div>
              
              <div className="flex items-center space-x-4 pt-4">
                <span className={`text-xs px-2 py-1 rounded-full uppercase font-bold ${
                  selectedRisk.severity === 'critical' 
                    ? 'bg-red-900/50 text-red-400' 
                    : selectedRisk.severity === 'high' 
                    ? 'bg-yellow-900/50 text-yellow-400' 
                    : 'bg-blue-900/50 text-blue-400'
                }`}>
                  {selectedRisk.severity} severity
                </span>
                <span className="text-xs text-gray-400">
                  Priority: {selectedRisk.priority}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RiskTab;