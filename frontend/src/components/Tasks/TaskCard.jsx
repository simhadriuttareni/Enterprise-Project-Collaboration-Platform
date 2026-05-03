import React from 'react';
import { formatDistanceToNow } from 'date-fns';
import { Calendar, User, Edit2, Trash2, Flag } from 'lucide-react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

const TaskCard = ({ task, onEdit, onDelete }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging
  } = useSortable({ id: task.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const getPriorityColor = (priority) => {
    switch(priority) {
      case 'urgent': return 'bg-red-100 text-red-700 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-700 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const isOverdue = task.is_overdue && task.status !== 'done';

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className={`bg-white rounded-lg p-4 shadow-sm border border-gray-200 hover:shadow-md transition-all cursor-grab active:cursor-grabbing ${
        isOverdue ? 'border-red-300 bg-red-50/30' : ''
      }`}
    >
      <div className="flex items-start justify-between mb-2">
        <h4 className="font-medium text-gray-900 flex-1 line-clamp-2">{task.title}</h4>
        <div className="flex items-center gap-1 ml-2">
          <button
            onClick={(e) => { e.stopPropagation(); onEdit(); }}
            className="p-1 rounded hover:bg-gray-100 transition-colors"
          >
            <Edit2 className="w-3 h-3 text-gray-400" />
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); onDelete(); }}
            className="p-1 rounded hover:bg-red-50 transition-colors"
          >
            <Trash2 className="w-3 h-3 text-gray-400 hover:text-red-500" />
          </button>
        </div>
      </div>
      
      {task.description && (
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">{task.description}</p>
      )}
      
      <div className="flex flex-wrap items-center gap-2 text-xs text-gray-500">
        <span className={`badge ${getPriorityColor(task.priority)}`}>
          <Flag className="w-3 h-3 inline mr-1" />
          {task.priority}
        </span>
        
        {task.due_date && (
          <span className={`flex items-center gap-1 ${isOverdue ? 'text-red-600 font-medium' : ''}`}>
            <Calendar className="w-3 h-3" />
            {formatDistanceToNow(new Date(task.due_date), { addSuffix: true })}
          </span>
        )}
        
        {task.assignee_id && (
          <span className="flex items-center gap-1">
            <User className="w-3 h-3" />
            Assigned
          </span>
        )}
      </div>
    </div>
  );
};

export default TaskCard;