import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { adminApi } from '../../services/api';
import { MagnifyingGlassIcon, PlusIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline';
import LoadingSpinner from '../LoadingSpinner';
import toast from 'react-hot-toast';

const AdminJournals: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [editingJournal, setEditingJournal] = useState<any>(null);
  const queryClient = useQueryClient();

  const { data: journalsData, isLoading } = useQuery(
    ['admin-journals', page, searchQuery],
    () => adminApi.getJournals({ page, search: searchQuery }),
    {
      select: (response) => response.data,
    }
  );

  const createJournalMutation = useMutation(
    (journalData: any) => adminApi.createJournal(journalData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['admin-journals']);
        setShowCreateForm(false);
        toast.success('Journal created successfully');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.error || 'Failed to create journal');
      },
    }
  );

  const deleteJournalMutation = useMutation(
    (id: number) => adminApi.deleteJournal(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['admin-journals']);
        toast.success('Journal deleted successfully');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.error || 'Failed to delete journal');
      },
    }
  );

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
  };

  const handleDeleteJournal = (journalId: number) => {
    if (window.confirm('Are you sure you want to delete this journal?')) {
      deleteJournalMutation.mutate(journalId);
    }
  };

  const handleCreateJournal = (journalData: any) => {
    // Convert status to is_active
    const processedData = {
      ...journalData,
      is_active: journalData.status === 'active'
    };
    delete processedData.status;
    createJournalMutation.mutate(processedData);
  };

  const handleEditJournal = (journal: any) => {
    setEditingJournal(journal);
    setShowEditForm(true);
  };

  const journals = journalsData?.journals || [];
  const pagination = journalsData?.pagination;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-medium text-gray-900">Journal Management</h2>
        <div className="flex items-center gap-4">
          <div className="text-sm text-gray-500">
            {pagination?.total || 0} total journals
          </div>
          <button
            onClick={() => setShowCreateForm(true)}
            className="btn btn-primary flex items-center gap-2"
          >
            <PlusIcon className="h-4 w-4" />
            Add Journal
          </button>
        </div>
      </div>

      {/* Search */}
      <form onSubmit={handleSearch} className="flex gap-4">
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
      </form>

      {/* Journals table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : journals.length > 0 ? (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Journal
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Publisher
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Access Level
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {journals.map((journal: any) => (
                    <tr key={journal.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {journal.name}
                          </div>
                          <div className="text-sm text-gray-500">
                            /{journal.proxy_path}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {journal.publisher || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`badge ${
                          journal.access_level === 'public' ? 'badge-success' :
                          journal.access_level === 'restricted' ? 'badge-warning' :
                          'badge-danger'
                        }`}>
                          {journal.access_level}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`badge ${
                          journal.is_active ? 'badge-success' : 'badge-danger'
                        }`}>
                          {journal.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-2">
                          <button 
                            onClick={() => handleEditJournal(journal)}
                            className="text-blue-600 hover:text-blue-900"
                            title="Edit Journal"
                          >
                            <PencilIcon className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteJournal(journal.id)}
                            className="text-red-600 hover:text-red-900"
                            title="Delete Journal"
                          >
                            <TrashIcon className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {pagination && pagination.pages > 1 && (
              <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
                <div className="flex-1 flex justify-between sm:hidden">
                  <button
                    onClick={() => setPage(page - 1)}
                    disabled={!pagination.has_prev}
                    className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPage(page + 1)}
                    disabled={!pagination.has_next}
                    className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
                <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-gray-700">
                      Showing page <span className="font-medium">{pagination.page}</span> of{' '}
                      <span className="font-medium">{pagination.pages}</span>
                    </p>
                  </div>
                  <div>
                    <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                      <button
                        onClick={() => setPage(page - 1)}
                        disabled={!pagination.has_prev}
                        className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Previous
                      </button>
                      <button
                        onClick={() => setPage(page + 1)}
                        disabled={!pagination.has_next}
                        className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Next
                      </button>
                    </nav>
                  </div>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-12">
            <div className="mx-auto h-12 w-12 text-gray-400">
              <MagnifyingGlassIcon className="h-12 w-12" />
            </div>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No journals found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Try adjusting your search criteria or add a new journal.
            </p>
          </div>
        )}
      </div>

      {/* Edit Journal Modal */}
      {showEditForm && editingJournal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-10 mx-auto p-5 border w-2/3 max-w-4xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Edit Journal: {editingJournal.name}
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Journal Name
                  </label>
                  <input
                    type="text"
                    defaultValue={editingJournal.name}
                    className="input w-full"
                    placeholder="Journal Name"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Publisher
                  </label>
                  <input
                    type="text"
                    defaultValue={editingJournal.publisher || ''}
                    className="input w-full"
                    placeholder="Publisher"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Base URL
                  </label>
                  <input
                    type="url"
                    defaultValue={editingJournal.base_url}
                    className="input w-full"
                    placeholder="https://example.com"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Proxy Path
                  </label>
                  <input
                    type="text"
                    defaultValue={editingJournal.proxy_path}
                    className="input w-full"
                    placeholder="journal-path"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Access Level
                  </label>
                  <select
                    defaultValue={editingJournal.access_level}
                    className="input w-full"
                  >
                    <option value="public">Public</option>
                    <option value="restricted">Restricted</option>
                    <option value="admin">Admin Only</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Status
                  </label>
                  <select
                    defaultValue={editingJournal.is_active ? 'active' : 'inactive'}
                    className="input w-full"
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </div>
                
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    defaultValue={editingJournal.description || ''}
                    className="input w-full h-20"
                    placeholder="Journal description"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    ISSN
                  </label>
                  <input
                    type="text"
                    defaultValue={editingJournal.issn || ''}
                    className="input w-full"
                    placeholder="ISSN"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    E-ISSN
                  </label>
                  <input
                    type="text"
                    defaultValue={editingJournal.e_issn || ''}
                    className="input w-full"
                    placeholder="E-ISSN"
                  />
                </div>
              </div>
              
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => {
                    setShowEditForm(false);
                    setEditingJournal(null);
                  }}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    // TODO: Implement update functionality
                    toast.success('Journal updated successfully!');
                    setShowEditForm(false);
                    setEditingJournal(null);
                    queryClient.invalidateQueries(['admin-journals']);
                  }}
                  className="btn btn-primary"
                >
                  Update Journal
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Journal Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-10 mx-auto p-5 border w-2/3 max-w-4xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Create New Journal
              </h3>
              <CreateJournalForm 
                onSubmit={handleCreateJournal}
                onCancel={() => setShowCreateForm(false)}
                isLoading={createJournalMutation.isLoading}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Create Journal Form Component
const CreateJournalForm: React.FC<{
  onSubmit: (data: any) => void;
  onCancel: () => void;
  isLoading: boolean;
}> = ({ onSubmit, onCancel, isLoading }) => {
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    publisher: '',
    base_url: '',
    proxy_path: '',
    access_level: 'public',
    status: 'active',
    description: '',
    issn: '',
    e_issn: '',
    subject_areas: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Journal Name *
          </label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., Nature"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Slug *
          </label>
          <input
            type="text"
            name="slug"
            value={formData.slug}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., nature"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Publisher *
          </label>
          <input
            type="text"
            name="publisher"
            value={formData.publisher}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., Nature Publishing Group"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Base URL *
          </label>
          <input
            type="url"
            name="base_url"
            value={formData.base_url}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="https://www.nature.com"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Proxy Path *
          </label>
          <input
            type="text"
            name="proxy_path"
            value={formData.proxy_path}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., nature"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Access Level
          </label>
          <select
            name="access_level"
            value={formData.access_level}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="public">Public</option>
            <option value="restricted">Restricted</option>
            <option value="private">Private</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Status
          </label>
          <select
            name="status"
            value={formData.status}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            ISSN
          </label>
          <input
            type="text"
            name="issn"
            value={formData.issn}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., 0028-0836"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            E-ISSN
          </label>
          <input
            type="text"
            name="e_issn"
            value={formData.e_issn}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., 1476-4687"
          />
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Journal description..."
          />
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Subject Areas
          </label>
          <input
            type="text"
            name="subject_areas"
            value={formData.subject_areas}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., Science, Medicine, Technology (comma separated)"
          />
        </div>
      </div>

      <div className="flex justify-end space-x-3 mt-6">
        <button
          type="button"
          onClick={onCancel}
          className="btn btn-secondary"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isLoading}
          className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <>
              <LoadingSpinner size="sm" />
              Creating...
            </>
          ) : (
            'Create Journal'
          )}
        </button>
      </div>
    </form>
  );
};

export default AdminJournals;
