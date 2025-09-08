import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { journalsApi } from '../services/api';
import { Journal, JournalSearchFilters } from '../types/journal';
import { MagnifyingGlassIcon, FunnelIcon } from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/LoadingSpinner';

const Journals: React.FC = () => {
  const [filters, setFilters] = useState<JournalSearchFilters>({});
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  const { data: journalsData, isLoading } = useQuery(
    ['journals', filters],
    () => journalsApi.getJournals({
      search: filters.search,
      subject_area: filters.subject_areas?.[0],
      access_level: filters.access_level,
    }),
    {
      select: (response) => response.data,
    }
  );

  const { data: subjectAreas } = useQuery(
    'subject-areas',
    () => journalsApi.getSubjectAreas(),
    {
      select: (response) => response.data.subject_areas,
    }
  );

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setFilters({ ...filters, search: searchQuery });
  };

  const handleFilterChange = (key: keyof JournalSearchFilters, value: any) => {
    setFilters({ ...filters, [key]: value });
  };

  const clearFilters = () => {
    setFilters({});
    setSearchQuery('');
  };

  const journals = journalsData?.journals || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Journals</h1>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="btn btn-secondary flex items-center gap-2"
        >
          <FunnelIcon className="h-4 w-4" />
          Filters
        </button>
      </div>

      {/* Search and filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleSearch} className="mb-4">
          <div className="flex gap-4">
            <div className="flex-1">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search journals..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="input pl-10"
                />
              </div>
            </div>
            <button type="submit" className="btn btn-primary">
              Search
            </button>
          </div>
        </form>

        {showFilters && (
          <div className="border-t border-gray-200 pt-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Access Level
                </label>
                <select
                  value={filters.access_level || ''}
                  onChange={(e) => handleFilterChange('access_level', e.target.value || undefined)}
                  className="input"
                >
                  <option value="">All levels</option>
                  <option value="public">Public</option>
                  <option value="restricted">Restricted</option>
                  <option value="admin">Admin only</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Subject Area
                </label>
                <select
                  value={filters.subject_areas?.[0] || ''}
                  onChange={(e) => handleFilterChange('subject_areas', e.target.value ? [e.target.value] : undefined)}
                  className="input"
                >
                  <option value="">All subjects</option>
                  {subjectAreas?.map((area: string) => (
                    <option key={area} value={area}>
                      {area}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Publisher
                </label>
                <input
                  type="text"
                  placeholder="Publisher name"
                  value={filters.publisher || ''}
                  onChange={(e) => handleFilterChange('publisher', e.target.value || undefined)}
                  className="input"
                />
              </div>
            </div>

            <div className="mt-4 flex gap-2">
              <button onClick={clearFilters} className="btn btn-secondary">
                Clear filters
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Results */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : journals.length > 0 ? (
          <>
            <div className="px-6 py-4 border-b border-gray-200">
              <p className="text-sm text-gray-600">
                Showing {journals.length} of {journalsData?.pagination.total || 0} journals
              </p>
            </div>
            <div className="divide-y divide-gray-200">
              {journals.map((journal: Journal) => (
                <div key={journal.id} className="p-6 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        {journal.name}
                      </h3>
                      {journal.publisher && (
                        <p className="text-sm text-gray-600 mb-2">
                          Published by {journal.publisher}
                        </p>
                      )}
                      {journal.description && (
                        <p className="text-sm text-gray-500 mb-3">
                          {journal.description}
                        </p>
                      )}
                      <div className="flex items-center gap-4">
                        <span className={`badge ${
                          journal.access_level === 'public' ? 'badge-success' :
                          journal.access_level === 'restricted' ? 'badge-warning' :
                          'badge-danger'
                        }`}>
                          {journal.access_level}
                        </span>
                        {journal.subject_areas && (() => {
                          const areas = Array.isArray(journal.subject_areas) 
                            ? journal.subject_areas 
                            : typeof journal.subject_areas === 'string' 
                              ? [journal.subject_areas] 
                              : [];
                          
                          return areas.length > 0 && (
                            <div className="flex gap-1">
                              {areas.slice(0, 3).map((area: string) => (
                                <span key={area} className="badge badge-primary text-xs">
                                  {area}
                                </span>
                              ))}
                              {areas.length > 3 && (
                                <span className="text-xs text-gray-500">
                                  +{areas.length - 3} more
                                </span>
                              )}
                            </div>
                          );
                        })()}
                      </div>
                    </div>
                    <div className="ml-4">
                      <Link
                        to={`/journals/${journal.id}`}
                        className="btn btn-primary"
                      >
                        View Details
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="text-center py-12">
            <div className="mx-auto h-12 w-12 text-gray-400">
              <MagnifyingGlassIcon className="h-12 w-12" />
            </div>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No journals found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Try adjusting your search criteria or filters.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Journals;
