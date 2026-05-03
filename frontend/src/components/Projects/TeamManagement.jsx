import React, { useState, useEffect } from 'react';
import { getProjectMembers, addTeamMember, removeTeamMember } from '../../services/project';
import { searchUsers } from '../../services/user';
import { Users, UserPlus, X, Mail, UserCheck } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';

const TeamManagement = ({ projectId }) => {
  const [members, setMembers] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMembers();
  }, [projectId]);

  const fetchMembers = async () => {
    try {
      const data = await getProjectMembers(projectId);
      setMembers(data);
    } catch (error) {
      console.error('Failed to fetch members:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (searchQuery.length < 2) return;
    
    setSearching(true);
    try {
      const results = await searchUsers(searchQuery);
      // Filter out users already in project
      const filteredResults = results.filter(
        user => !members.some(member => member.user_id === user.id)
      );
      setSearchResults(filteredResults);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setSearching(false);
    }
  };

  const handleAddMember = async (userId, role = 'member') => {
    try {
      await addTeamMember(projectId, userId, role);
      toast.success('Member added successfully');
      fetchMembers();
      setShowAddModal(false);
      setSearchQuery('');
      setSearchResults([]);
    } catch (error) {
      toast.error('Failed to add member');
    }
  };

  const handleRemoveMember = async (userId) => {
    if (window.confirm('Are you sure you want to remove this member?')) {
      try {
        await removeTeamMember(projectId, userId);
        toast.success('Member removed');
        fetchMembers();
      } catch (error) {
        toast.error('Failed to remove member');
      }
    }
  };

  const AddMemberModal = () => (
    <AnimatePresence>
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/50"
            onClick={() => setShowAddModal(false)}
          />
          
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="relative bg-white rounded-2xl shadow-xl max-w-md w-full p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Add Team Member</h2>
              <button
                onClick={() => setShowAddModal(false)}
                className="p-1 rounded-lg hover:bg-gray-100"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="input-label">Search by email or username</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                    className="input-field flex-1"
                    placeholder="Enter email or username..."
                  />
                  <button
                    onClick={handleSearch}
                    disabled={searching}
                    className="btn-primary"
                  >
                    {searching ? '...' : 'Search'}
                  </button>
                </div>
              </div>

              {searchResults.length > 0 && (
                <div className="border rounded-lg divide-y">
                  {searchResults.map((user) => (
                    <div key={user.id} className="p-3 flex items-center justify-between hover:bg-gray-50">
                      <div>
                        <p className="font-medium text-gray-900">{user.full_name}</p>
                        <p className="text-sm text-gray-500">{user.email}</p>
                        <p className="text-xs text-gray-400">@{user.username}</p>
                      </div>
                      <button
                        onClick={() => handleAddMember(user.id)}
                        className="text-primary-600 hover:text-primary-700"
                      >
                        <UserPlus className="w-5 h-5" />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {searchQuery && searchResults.length === 0 && !searching && (
                <p className="text-center text-gray-500 py-4">No users found</p>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );

  if (loading) {
    return <div className="text-center py-4">Loading team...</div>;
  }

  return (
    <div className="bg-white rounded-2xl shadow-soft p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Users className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Team Members</h3>
          <span className="text-sm text-gray-500">({members.length})</span>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="text-primary-600 hover:text-primary-700 text-sm font-medium flex items-center gap-1"
        >
          <UserPlus className="w-4 h-4" />
          Add Member
        </button>
      </div>

      <div className="space-y-3">
        {members.length === 0 ? (
          <p className="text-center text-gray-500 py-4">No team members yet</p>
        ) : (
          members.map((member) => (
            <div key={member.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center">
                  <span className="text-white font-medium">
                    {member.full_name?.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div>
                  <p className="font-medium text-gray-900">{member.full_name}</p>
                  <p className="text-sm text-gray-500">{member.email}</p>
                  <p className="text-xs text-gray-400">@{member.username}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="badge bg-primary-100 text-primary-700">
                  {member.role}
                </span>
                <button
                  onClick={() => handleRemoveMember(member.user_id)}
                  className="p-1 rounded hover:bg-red-50 transition-colors"
                >
                  <X className="w-4 h-4 text-gray-400 hover:text-red-500" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      <AddMemberModal />
    </div>
  );
};

export default TeamManagement;