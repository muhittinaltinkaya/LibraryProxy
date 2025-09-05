import React from 'react';
import { useQuery } from 'react-query';
import { adminApi } from '../../services/api';
import { ChartBarIcon, ClockIcon, UsersIcon, BookOpenIcon } from '@heroicons/react/24/outline';
import LoadingSpinner from '../LoadingSpinner';

const AdminStats: React.FC = () => {
  const { data: stats, isLoading } = useQuery(
    'admin-stats',
    () => adminApi.getStats(),
    {
      select: (response) => response.data,
    }
  );

  const { data: accessLogs, isLoading: logsLoading } = useQuery(
    'admin-access-logs',
    () => adminApi.getAccessLogs({ per_page: 20 }),
    {
      select: (response) => response.data,
    }
  );

  if (isLoading || logsLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-blue-50 rounded-lg p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <UsersIcon className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-blue-600">Total Users</p>
              <p className="text-2xl font-semibold text-blue-900">
                {stats?.users.total || 0}
              </p>
              <p className="text-xs text-blue-600">
                {stats?.users.active || 0} active
              </p>
            </div>
          </div>
        </div>

        <div className="bg-green-50 rounded-lg p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <BookOpenIcon className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-green-600">Journals</p>
              <p className="text-2xl font-semibold text-green-900">
                {stats?.journals.total || 0}
              </p>
              <p className="text-xs text-green-600">
                {stats?.journals.active || 0} active
              </p>
            </div>
          </div>
        </div>

        <div className="bg-purple-50 rounded-lg p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-purple-600">Proxy Configs</p>
              <p className="text-2xl font-semibold text-purple-900">
                {stats?.proxy_configs.total || 0}
              </p>
              <p className="text-xs text-purple-600">
                {stats?.proxy_configs.active || 0} active
              </p>
            </div>
          </div>
        </div>

        <div className="bg-yellow-50 rounded-lg p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ClockIcon className="h-8 w-8 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-yellow-600">Access Logs</p>
              <p className="text-2xl font-semibold text-yellow-900">
                {stats?.access_logs.total || 0}
              </p>
              <p className="text-xs text-yellow-600">
                Total requests
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Access Logs */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Recent Access Logs</h2>
        </div>
        <div className="p-6">
          {accessLogs?.logs && accessLogs.logs.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Journal
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      IP Address
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Time
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {accessLogs.logs.map((log: any) => (
                    <tr key={log.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        User {log.user_id || 'Anonymous'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        Journal {log.journal_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {log.ip_address}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`badge ${
                          log.response_status >= 200 && log.response_status < 300
                            ? 'badge-success'
                            : log.response_status >= 400
                            ? 'badge-danger'
                            : 'badge-warning'
                        }`}>
                          {log.response_status || 'N/A'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(log.timestamp).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-sm text-gray-500">No access logs found</p>
          )}
        </div>
      </div>

      {/* System Health */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">System Health</h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">99.9%</div>
              <div className="text-sm text-gray-500">Uptime</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">45ms</div>
              <div className="text-sm text-gray-500">Avg Response Time</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">1.2GB</div>
              <div className="text-sm text-gray-500">Memory Usage</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminStats;
