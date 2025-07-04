import React from 'react';
import { BarChart3Icon, ShieldCheckIcon, FileTextIcon, AlertTriangleIcon, SettingsIcon, HelpCircleIcon, LogOutIcon } from 'lucide-react';
import logo from '../assets/logo.jpg';
const Sidebar = ({
  activeTab,
  setActiveTab
}) => {
  return <aside className="hidden md:flex flex-col w-64 bg-gray-800 border-r border-gray-700">
      <div className="p-4 border-b border-gray-700">
      {/* <img src={logo} alt="Logo" className="h-8 w-8 object-contain" /> */}
        <h2 className="text-xl font-bold text-white">Veritas</h2>
      </div>
      <nav className="flex-1 pt-4">
        <div className="px-4 mb-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
          Main
        </div>
        <a href="#" className={`flex items-center px-4 py-3 ${activeTab === 'dashboard' ? 'text-gray-300 bg-gray-700' : 'text-gray-400 hover:bg-gray-700 hover:text-gray-200 transition-colors'}`} onClick={e => {
        e.preventDefault();
        setActiveTab('dashboard');
      }}>
          <BarChart3Icon className="h-5 w-5 mr-3" />
          Dashboard
        </a>
        <a href="#" className={`flex items-center px-4 py-3 ${activeTab === 'compliance' ? 'text-gray-300 bg-gray-700' : 'text-gray-400 hover:bg-gray-700 hover:text-gray-200 transition-colors'}`} onClick={e => {
        e.preventDefault();
        setActiveTab('compliance');
      }}>
          <ShieldCheckIcon className="h-5 w-5 mr-3" />
          Compliance
        </a>
        <a href="#" className={`flex items-center px-4 py-3 ${activeTab === 'documents' ? 'text-gray-300 bg-gray-700' : 'text-gray-400 hover:bg-gray-700 hover:text-gray-200 transition-colors'}`} onClick={e => {
        e.preventDefault();
        setActiveTab('documents');
      }}>
          <FileTextIcon className="h-5 w-5 mr-3" />
          Documents
        </a>
        <a href="#" className={`flex items-center px-4 py-3 ${activeTab === 'risk' ? 'text-gray-300 bg-gray-700' : 'text-gray-400 hover:bg-gray-700 hover:text-gray-200 transition-colors'}`} onClick={e => {
        e.preventDefault();
        setActiveTab('risk');
      }}>
          <AlertTriangleIcon className="h-5 w-5 mr-3" />
          Risks
        </a>
        <div className="px-4 mt-6 mb-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
          Settings
        </div>
        <a href="#" className={`flex items-center px-4 py-3 ${activeTab === 'settings' ? 'text-gray-300 bg-gray-700' : 'text-gray-400 hover:bg-gray-700 hover:text-gray-200 transition-colors'}`} onClick={e => {
        e.preventDefault();
        setActiveTab('settings');
      }}>
          <SettingsIcon className="h-5 w-5 mr-3" />
          Preferences
        </a>
        <a href="#" className="flex items-center px-4 py-3 text-gray-400 hover:bg-gray-700 hover:text-gray-200 transition-colors">
          <HelpCircleIcon className="h-5 w-5 mr-3" />
          Help & Support
        </a>
      </nav>
      <div className="p-4 border-t border-gray-700">
        <a href="#" className="flex items-center text-gray-400 hover:text-gray-200">
          <LogOutIcon className="h-5 w-5 mr-3" />
          Sign Out
        </a>
      </div>
    </aside>;
};
export default Sidebar;