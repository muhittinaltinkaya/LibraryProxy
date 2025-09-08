import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { analyticsApi } from '../../services/api';
import { 
  ChartBarIcon, 
  UsersIcon, 
  DocumentTextIcon, 
  GlobeAltIcon,
  ExclamationTriangleIcon,
  ArrowDownTrayIcon
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../LoadingSpinner';

const AnalyticsDashboard: React.FC = () => {
  const [dateRange, setDateRange] = useState({
    start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0]
  });

  const { data: dashboardData, isLoading } = useQuery(
    ['analytics-dashboard', dateRange],
    () => analyticsApi.getDashboardStats(dateRange),
    {
      select: (response) => response.data,
    }
  );

  const { data: resourceData } = useQuery(
    ['analytics-resources', dateRange],
    () => analyticsApi.getResourceReport({ ...dateRange, limit: 10 }),
    {
      select: (response) => response.data,
    }
  );

  const { data: userData } = useQuery(
    ['analytics-users', dateRange],
    () => analyticsApi.getUserReport({ ...dateRange, limit: 10 }),
    {
      select: (response) => response.data,
    }
  );

  const { data: failureData } = useQuery(
    ['analytics-failures', dateRange],
    () => analyticsApi.getFailureAnalysis(dateRange),
    {
      select: (response) => response.data,
    }
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const stats = dashboardData?.general_stats || {};
  const topResources = resourceData?.resources || [];
  const topUsers = userData?.users || [];
  const failures = failureData?.failures || [];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h2>
        <div className="flex items-center gap-4">
          <input
            type="date"
            value={dateRange.start_date}
            onChange={(e) => setDateRange({ ...dateRange, start_date: e.target.value })}
            className="input"
          />
          <span className="text-gray-500">to</span>
          <input
            type="date"
            value={dateRange.end_date}
            onChange={(e) => setDateRange({ ...dateRange, end_date: e.target.value })}
            className="input"
          />
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <ChartBarIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Accesses</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total_accesses || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <UsersIcon className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Unique Users</p>
              <p className="text-2xl font-bold text-gray-900">{stats.unique_users || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <DocumentTextIcon className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Resources</p>
              <p className="text-2xl font-bold text-gray-900">{stats.unique_resources || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <ChartBarIcon className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Success Rate</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.success_rate ? `${stats.success_rate.toFixed(1)}%` : '0%'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Hourly Usage Pattern */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Hourly Usage Pattern</h3>
          <div className="h-64 flex items-end space-x-1">
            {dashboardData?.hourly_pattern?.map((hour: any, index: number) => (
              <div key={index} className="flex-1 flex flex-col items-center">
                <div
                  className="bg-blue-500 w-full rounded-t"
                  style={{ height: `${(hour.access_count / Math.max(...dashboardData.hourly_pattern.map((h: any) => h.access_count))) * 200}px` }}
                />
                <span className="text-xs text-gray-500 mt-2">{hour.hour}:00</span>
              </div>
            )) || <div className="text-gray-500">No data available</div>}
          </div>
        </div>

        {/* Daily Trend */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Daily Usage Trend</h3>
          <div className="h-64 flex items-end space-x-1">
            {dashboardData?.daily_trend?.slice(-14).map((day: any, index: number) => (
              <div key={index} className="flex-1 flex flex-col items-center">
                <div
                  className="bg-green-500 w-full rounded-t"
                  style={{ height: `${(day.access_count / Math.max(...dashboardData.daily_trend.map((d: any) => d.access_count))) * 200}px` }}
                />
                <span className="text-xs text-gray-500 mt-2">
                  {new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </span>
              </div>
            )) || <div className="text-gray-500">No data available</div>}
          </div>
        </div>
      </div>

      {/* Top Resources and Users */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Resources */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Top Resources</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {topResources.map((resource: any, index: number) => (
              <div key={index} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{resource.resource_name}</p>
                    <p className="text-sm text-gray-500">{resource.resource_provider}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">{resource.access_count}</p>
                    <p className="text-xs text-gray-500">accesses</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Users */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Top Users</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {topUsers.map((user: any, index: number) => (
              <div key={index} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      {user.first_name} {user.last_name}
                    </p>
                    <p className="text-sm text-gray-500">{user.department}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">{user.access_count}</p>
                    <p className="text-xs text-gray-500">accesses</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Failure Analysis */}
      {failures.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-500 mr-2" />
              Failure Analysis
            </h3>
          </div>
          <div className="divide-y divide-gray-200">
            {failures.map((failure: any, index: number) => (
              <div key={index} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{failure.auth_failure_reason}</p>
                    <p className="text-sm text-gray-500">{failure.denial_reason}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">{failure.failure_count}</p>
                    <p className="text-xs text-gray-500">failures</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard;
