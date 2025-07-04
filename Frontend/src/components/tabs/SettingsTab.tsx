import React from 'react';
import { SettingsIcon, SunIcon, MoonIcon, BellIcon, UserIcon, LockIcon } from 'lucide-react';
import { useTheme } from '../ThemeContext';
const SettingsTab = () => {
  const {
    theme,
    toggleTheme
  } = useTheme();
  return <div>
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center">
          <SettingsIcon className="mr-3 h-8 w-8 text-blue-400" />
          Settings
        </h1>
        <p className="text-gray-400 mt-2">
          Customize your compliance dashboard experience
        </p>
      </header>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-gray-800 rounded-xl p-6">
            <h2 className="text-xl font-bold text-white mb-4">Appearance</h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-400 mb-2">Theme</p>
                <div className="flex items-center">
                  <button className={`flex items-center px-4 py-2 rounded-l-lg border ${theme === 'light' ? 'bg-blue-600 border-blue-500 text-white' : 'bg-gray-700 border-gray-600 text-gray-300'}`} onClick={() => theme === 'dark' && toggleTheme()}>
                    <SunIcon className="h-4 w-4 mr-2" />
                    Light
                  </button>
                  <button className={`flex items-center px-4 py-2 rounded-r-lg border ${theme === 'dark' ? 'bg-blue-600 border-blue-500 text-white' : 'bg-gray-700 border-gray-600 text-gray-300'}`} onClick={() => theme === 'light' && toggleTheme()}>
                    <MoonIcon className="h-4 w-4 mr-2" />
                    Dark
                  </button>
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-400 mb-2">Sidebar Position</p>
                <select className="bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option value="left">Left</option>
                  <option value="right">Right</option>
                </select>
              </div>
              <div>
                <p className="text-sm text-gray-400 mb-2">
                  Default Dashboard View
                </p>
                <select className="bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option value="overview">Overview</option>
                  <option value="compliance">Compliance</option>
                  <option value="risk">Risk Analysis</option>
                </select>
              </div>
            </div>
          </div>
          <div className="bg-gray-800 rounded-xl p-6">
            <h2 className="text-xl font-bold text-white mb-4">Notifications</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <BellIcon className="h-5 w-5 text-gray-400 mr-3" />
                  <span>Email Alerts</span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" value="" className="sr-only peer" defaultChecked />
                  <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <BellIcon className="h-5 w-5 text-gray-400 mr-3" />
                  <span>Critical Risk Alerts</span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" value="" className="sr-only peer" defaultChecked />
                  <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <BellIcon className="h-5 w-5 text-gray-400 mr-3" />
                  <span>Weekly Reports</span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" value="" className="sr-only peer" />
                  <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>
          </div>
        </div>
        <div className="space-y-6">
          <div className="bg-gray-800 rounded-xl p-6">
            <h2 className="text-xl font-bold text-white mb-4">Account</h2>
            <div className="flex items-center mb-4">
              <div className="bg-blue-900 rounded-full p-3">
                <UserIcon className="h-6 w-6 text-blue-400" />
              </div>
              <div className="ml-3">
                <p className="font-medium">John Doe</p>
                <p className="text-sm text-gray-400">Administrator</p>
              </div>
            </div>
            <div className="space-y-2">
              <button className="flex items-center text-sm text-blue-400 hover:text-blue-300">
                <UserIcon className="h-4 w-4 mr-2" />
                Edit Profile
              </button>
              <button className="flex items-center text-sm text-blue-400 hover:text-blue-300">
                <LockIcon className="h-4 w-4 mr-2" />
                Change Password
              </button>
            </div>
          </div>
          <div className="bg-gray-800 rounded-xl p-6">
            <h2 className="text-xl font-bold text-white mb-4">API Access</h2>
            <p className="text-sm text-gray-400 mb-3">
              Generate API keys to access compliance data programmatically
            </p>
            <button className="w-full bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2 text-sm">
              Generate API Key
            </button>
          </div>
        </div>
      </div>
    </div>;
};
export default SettingsTab;