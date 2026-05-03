import React from 'react';
import { formatDistanceToNow } from 'date-fns';
import { CheckCircle2, Circle, Clock, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

const RecentTasks = ({ tasks }) => {
  const getStatusIcon = (status) => {
    switch(status) {
      case 'done':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case 'in_progress':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      default:
        return <Circle className="w-4 h-4 text-gray-400" />;
    }
  };

  const getPriorityColor = (priority) => {
    switch(priority) {
      case 'urgent': return 'bg-red-100 text-red-700';
      case 'high': return 'bg-orange-100 text-orange-700';
      case 'medium': return 'bg-yellow-100 text-yellow-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="bg-white rounded-2xl shadow-soft p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Recent Tasks</h3>
        <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
          View All
        </button>
      </div>
      
      <div className="space-y-3">
        {tasks.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No tasks yet. Create your first task!
          </div>
        ) : (
          tasks.map((task, idx) => (
            <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
              <div className="flex items-center gap-3 flex-1">
                {getStatusIcon(task.status)}
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{task.title}</p>
                  <p className="text-xs text-gray-500">
                    {task.due_date && `Due ${formatDistanceToNow(new Date(task.due_date), { addSuffix: true })}`}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`badge ${getPriorityColor(task.priority)}`}>
                  {task.priority}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </motion.div>
  );
};

export default RecentTasks;