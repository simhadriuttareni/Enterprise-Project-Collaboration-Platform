import React from 'react';
import { AlertCircle, X } from 'lucide-react';
import { motion } from 'framer-motion';

const ErrorAlert = ({ message, onClose }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="bg-error-50 border border-error-200 rounded-lg p-4 mb-4"
    >
      <div className="flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-error-500 mt-0.5" />
        <p className="text-sm text-error-700 flex-1">{message}</p>
        <button onClick={onClose} className="text-error-500 hover:text-error-700">
          <X className="w-4 h-4" />
        </button>
      </div>
    </motion.div>
  );
};

export default ErrorAlert;