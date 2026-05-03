import api from './api';

export const getProjects = async (skip = 0, limit = 100, archived = false) => {
  const response = await api.get('/projects/', { params: { skip, limit, archived } });
  return response.data;
};

export const createProject = async (projectData) => {
  const response = await api.post('/projects/', projectData);
  return response.data;
};

export const getProject = async (id) => {
  const response = await api.get(`/projects/${id}`);
  return response.data;
};

export const updateProject = async (id, projectData) => {
  const response = await api.put(`/projects/${id}`, projectData);
  return response.data;
};

export const deleteProject = async (id) => {
  await api.delete(`/projects/${id}`);
};

export const addTeamMember = async (projectId, userId, role) => {
  const response = await api.post(`/projects/${projectId}/members/${userId}`, null, {
    params: { role }
  });
  return response.data;
};

export const removeTeamMember = async (projectId, userId) => {
  await api.delete(`/projects/${projectId}/members/${userId}`);
};

export const getProjectMembers = async (projectId) => {
  const response = await api.get(`/projects/${projectId}/members`);
  return response.data;
};