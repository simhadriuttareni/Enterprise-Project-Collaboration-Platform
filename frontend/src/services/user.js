import api from './api';

/**
 * Search for users by email or username
 * @param {string} query - Search query (email or username)
 * @returns {Promise<Array>} List of matching users
 */
export const searchUsers = async (query) => {
    try {
        if (!query || query.length < 2) {
            return [];
        }
        const response = await api.get('/users/search', { 
            params: { q: query } 
        });
        return response.data;
    } catch (error) {
        console.error('Search users error:', error);
        if (error.response?.status === 401) {
            console.log('Authentication required for user search');
        }
        return [];
    }
};

/**
 * Get current user profile
 * @returns {Promise<Object>} User profile data
 */
export const getUserProfile = async () => {
    try {
        const response = await api.get('/users/me');
        return response.data;
    } catch (error) {
        console.error('Get user profile error:', error);
        throw error;
    }
};

/**
 * Update current user profile
 * @param {Object} userData - User data to update
 * @returns {Promise<Object>} Updated user profile
 */
export const updateUserProfile = async (userData) => {
    try {
        const response = await api.put('/users/me', userData);
        return response.data;
    } catch (error) {
        console.error('Update user profile error:', error);
        throw error;
    }
};

/**
 * Get user by ID
 * @param {number} userId - User ID
 * @returns {Promise<Object>} User data
 */
export const getUserById = async (userId) => {
    try {
        // Note: You might need to add this endpoint to backend
        const response = await api.get(`/users/${userId}`);
        return response.data;
    } catch (error) {
        console.error('Get user by ID error:', error);
        return null;
    }
};