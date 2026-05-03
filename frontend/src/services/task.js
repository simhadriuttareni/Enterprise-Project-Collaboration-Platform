import api from './api';

export const getTasks = async (projectId, filters = {}) => {
  const params = { ...filters };
  const response = await api.get(`/tasks/project/${projectId}`, { params });
  return response.data;
};

export const createTask = async (taskData) => {
  const response = await api.post('/tasks/', taskData);
  return response.data;
};

export const getTask = async (id) => {
  const response = await api.get(`/tasks/${id}`);
  return response.data;
};

export const updateTask = async (id, taskData) => {
  const response = await api.put(`/tasks/${id}`, taskData);
  return response.data;
};

export const deleteTask = async (id) => {
  await api.delete(`/tasks/${id}`);
};

export const assignTask = async (taskId, userId) => {
  const response = await api.post(`/tasks/${taskId}/assign/${userId}`);
  return response.data;
};

export const getOverdueTasks = async () => {
  const response = await api.get('/tasks/dashboard/overdue');
  return response.data;
};