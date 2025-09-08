import React from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { journalsApi } from '../services/api';
import { BookOpenIcon, ClockIcon, UserGroupIcon } from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/LoadingSpinner';
import { Journal } from '../types/journal';

const Dashboard: React.FC = () => {
  const { data: journalsData, isLoading: journalsLoading } = useQuery(
    'recent-journals',
    () => journalsApi.getJournals({ per_page: 6 }),
    {
      select: (response) => response.data,
    }
  );

  const { data: subjectAreas, isLoading: areasLoading } = useQuery(
    'subject-areas',
    () => journalsApi.getSubjectAreas(),
    {
      select: (response) => response.data.subject_areas,
    }
  );

  if (journalsLoading || areasLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const journals: Journal[] = journalsData?.journals || [];
  const areas: string[] = subjectAreas || [];

  return (
    <div className="space-y-6">
      {/* Welcome section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Welcome to LibProxy
        </h1>
        <p className="text-gray-600">
          Access electronic journals through our dynamic proxy system. 
          Browse available journals and get instant access to academic resources.
        </p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <BookOpenIcon className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Available Journals</p>
              <p className="text-2xl font-semibold text-gray-900">
                {journalsData?.pagination.total || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <UserGroupIcon className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Subject Areas</p>
              <p className="text-2xl font-semibold text-gray-900">{areas.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ClockIcon className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Active Sessions</p>
              <p className="text-2xl font-semibold text-gray-900">-</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent journals */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-medium text-gray-900">Recent Journals</h2>
            <Link
              to="/journals"
              className="text-sm font-medium text-blue-600 hover:text-blue-500"
            >
              View all
            </Link>
          </div>
        </div>
        <div className="p-6">
          {journals.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {journals.map((journal) => (
                <div
                  key={journal.id}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <h3 className="font-medium text-gray-900 mb-2">{journal.name}</h3>
                  {journal.publisher && (
                    <p className="text-sm text-gray-600 mb-2">{journal.publisher}</p>
                  )}
                  {journal.description && (
                    <p className="text-sm text-gray-500 mb-3 line-clamp-2">
                      {journal.description}
                    </p>
                  )}
                  <div className="flex items-center justify-between">
                    <span className={`badge ${
                      journal.access_level === 'public' ? 'badge-success' :
                      journal.access_level === 'restricted' ? 'badge-warning' :
                      'badge-danger'
                    }`}>
                      {journal.access_level}
                    </span>
                    <Link
                      to={`/journals/${journal.id}`}
                      className="text-sm text-blue-600 hover:text-blue-500"
                    >
                      View details →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <BookOpenIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No journals found</h3>
              <p className="mt-1 text-sm text-gray-500">
                There are no journals available at the moment.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Subject areas */}
      {areas.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Subject Areas</h2>
          </div>
          <div className="p-6">
            <div className="flex flex-wrap gap-2">
              {areas.slice(0, 10).map((area) => (
                <span
                  key={area}
                  className="badge badge-primary"
                >
                  {area}
                </span>
              ))}
              {areas.length > 10 && (
                <span className="text-sm text-gray-500">
                  +{areas.length - 10} more
                </span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
