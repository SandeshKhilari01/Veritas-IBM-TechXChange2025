import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip } from 'recharts';
import { getComplianceSummary } from '../api';

interface ComplianceData {
  summary: {
    rules_checked: number;
    passed: number;
    warnings: number;
    failures: number;
  };
  severity_data: Array<{
    name: string;
    value: number;
    color: string;
  }>;
  total_issues: number;
}

const ComplianceSummary = () => {
  const [data, setData] = useState<ComplianceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await getComplianceSummary();
        if (response.success) {
          setData(response);
        } else {
          setError(response.error || 'Failed to fetch compliance data');
        }
      } catch (err) {
        setError('Failed to connect to the server');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-xl p-6">
        <h2 className="text-xl font-bold text-white mb-4">Compliance Summary</h2>
        <div className="animate-pulse">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-gray-700 rounded-lg p-4 text-center">
                <div className="h-4 bg-gray-600 rounded mb-2"></div>
                <div className="h-8 bg-gray-600 rounded"></div>
              </div>
            ))}
          </div>
          <div className="h-64 bg-gray-700 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-800 rounded-xl p-6">
        <h2 className="text-xl font-bold text-white mb-4">Compliance Summary</h2>
        <div className="text-red-400 text-center py-8">
          {error}
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-gray-800 rounded-xl p-6">
        <h2 className="text-xl font-bold text-white mb-4">Compliance Summary</h2>
        <div className="text-gray-400 text-center py-8">
          No compliance data available. Please run analysis first.
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-xl p-6">
      <h2 className="text-xl font-bold text-white mb-4">Compliance Summary</h2>
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-700 rounded-lg p-4 text-center">
          <p className="text-sm text-gray-400">Rules Checked</p>
          <p className="text-2xl font-bold mt-1">{data.summary.rules_checked}</p>
        </div>
        <div className="bg-gray-700 rounded-lg p-4 text-center">
          <p className="text-sm text-gray-400">Passed</p>
          <p className="text-2xl font-bold mt-1 text-green-400">{data.summary.passed}</p>
        </div>
        <div className="bg-gray-700 rounded-lg p-4 text-center">
          <p className="text-sm text-gray-400">Warnings</p>
          <p className="text-2xl font-bold mt-1 text-yellow-400">{data.summary.warnings}</p>
        </div>
        <div className="bg-gray-700 rounded-lg p-4 text-center">
          <p className="text-sm text-gray-400">Failures</p>
          <p className="text-2xl font-bold mt-1 text-red-400">{data.summary.failures}</p>
        </div>
      </div>
      <div className="mt-6">
        <h3 className="text-lg font-medium text-white mb-3">
          Severity Breakdown
        </h3>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart 
              data={data.severity_data} 
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
              <Bar dataKey="value" fill="#3B82F6">
                {data.severity_data.map((entry, index) => (
                  <Bar key={`cell-${index}`} dataKey="value" fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default ComplianceSummary;