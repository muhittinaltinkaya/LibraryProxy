import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import { journalsApi } from '../services/api';
import { Journal } from '../types/journal';
import { BookOpenIcon, ArrowTopRightOnSquareIcon, ClockIcon } from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';

const JournalDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [isRequestingAccess, setIsRequestingAccess] = useState(false);

  const { data: journalData, isLoading } = useQuery(
    ['journal', id],
    () => journalsApi.getJournal(Number(id)),
    {
      select: (response) => response.data.journal,
      enabled: !!id,
    }
  );

  const handleRequestAccess = async () => {
    if (!journalData) return;
    
    setIsRequestingAccess(true);
    try {
      // Generate proxy URL
      const proxyUrl = `http://localhost:80/${journalData.proxy_path}`;
      
      // Open the journal content in a new tab
      window.open(proxyUrl, '_blank');
      toast.success('Opening journal content in new tab');
    } catch (error) {
      toast.error('Failed to open journal content');
    } finally {
      setIsRequestingAccess(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!journalData) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900">Journal not found</h3>
        <p className="mt-1 text-sm text-gray-500">
          The journal you're looking for doesn't exist or has been removed.
        </p>
        <button
          onClick={() => navigate('/journals')}
          className="mt-4 btn btn-primary"
        >
          Back to Journals
        </button>
      </div>
    );
  }

  const journal: Journal = journalData;

  return (
    <div className="space-y-6">
      {/* Back button */}
      <button
        onClick={() => navigate('/journals')}
        className="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-1"
      >
        ← Back to Journals
      </button>

      {/* Journal header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {journal.name}
            </h1>
            {journal.publisher && (
              <p className="text-lg text-gray-600 mb-4">
                Published by {journal.publisher}
              </p>
            )}
            {journal.description && (
              <p className="text-gray-700 mb-4">{journal.description}</p>
            )}
            
            <div className="flex items-center gap-4 mb-4">
              <span className={`badge ${
                journal.access_level === 'public' ? 'badge-success' :
                journal.access_level === 'restricted' ? 'badge-warning' :
                'badge-danger'
              }`}>
                {journal.access_level}
              </span>
              {journal.requires_auth && (
                <span className="badge badge-primary">
                  Authentication Required
                </span>
              )}
            </div>

            {journal.subject_areas && journal.subject_areas.length > 0 && (
              <div className="mb-4">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Subject Areas</h3>
                <div className="flex flex-wrap gap-2">
                  {journal.subject_areas.map((area) => (
                    <span key={area} className="badge badge-primary">
                      {area}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          <div className="ml-6">
            <BookOpenIcon className="h-16 w-16 text-gray-400" />
          </div>
        </div>
      </div>

      {/* Journal details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Basic information */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Journal Information</h2>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Base URL</dt>
              <dd className="text-sm text-gray-900 break-all">{journal.base_url}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Proxy Path</dt>
              <dd className="text-sm text-gray-900">/{journal.proxy_path}</dd>
            </div>
            {journal.issn && (
              <div>
                <dt className="text-sm font-medium text-gray-500">ISSN</dt>
                <dd className="text-sm text-gray-900">{journal.issn}</dd>
              </div>
            )}
            {journal.e_issn && (
              <div>
                <dt className="text-sm font-medium text-gray-500">E-ISSN</dt>
                <dd className="text-sm text-gray-900">{journal.e_issn}</dd>
              </div>
            )}
            <div>
              <dt className="text-sm font-medium text-gray-500">Authentication Method</dt>
              <dd className="text-sm text-gray-900 capitalize">{journal.auth_method}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Timeout</dt>
              <dd className="text-sm text-gray-900">{journal.timeout} seconds</dd>
            </div>
          </dl>
        </div>

        {/* Access information */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Access Information</h2>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <ClockIcon className="h-5 w-5 text-gray-400" />
              <div>
                <p className="text-sm font-medium text-gray-900">Created</p>
                <p className="text-sm text-gray-500">
                  {new Date(journal.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <ArrowTopRightOnSquareIcon className="h-5 w-5 text-gray-400" />
              <div>
                <p className="text-sm font-medium text-gray-900">Last Updated</p>
                <p className="text-sm text-gray-500">
                  {new Date(journal.updated_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>

          <div className="mt-6">
            <button
              onClick={handleRequestAccess}
              disabled={isRequestingAccess || !journal.is_active}
              className="w-full btn btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isRequestingAccess ? (
                <>
                  <LoadingSpinner size="sm" />
                  Opening Journal...
                </>
              ) : (
                <>
                  <ArrowTopRightOnSquareIcon className="h-4 w-4" />
                  View Journal Content
                </>
              )}
            </button>
            
            {!journal.is_active && (
              <p className="mt-2 text-sm text-red-600 text-center">
                This journal is currently unavailable
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Custom headers */}
      {journal.custom_headers && Object.keys(journal.custom_headers).length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Custom Headers</h2>
          <div className="bg-gray-50 rounded-lg p-4">
            <pre className="text-sm text-gray-700 overflow-x-auto">
              {JSON.stringify(journal.custom_headers, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default JournalDetail;
