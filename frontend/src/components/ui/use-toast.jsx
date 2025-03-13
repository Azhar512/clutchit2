import React, { createContext, useContext, useState } from 'react';

const ToastContext = createContext({});

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const toast = ({ title, description, duration = 5000 }) => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts((prev) => [...prev, { id, title, description }]);
    
    if (duration !== Infinity) {
      setTimeout(() => {
        setToasts((prev) => prev.filter((toast) => toast.id !== id));
      }, duration);
    }
    
    return { id, dismiss: () => setToasts((prev) => prev.filter((t) => t.id !== id)) };
  };

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="fixed bottom-0 right-0 z-50 flex flex-col p-4 space-y-4 max-w-md">
        {toasts.map((t) => (
          <div 
            key={t.id}
            className="bg-white rounded-lg border shadow-lg p-4 flex flex-col gap-1 animate-in fade-in"
          >
            {t.title && <div className="font-semibold">{t.title}</div>}
            {t.description && <div className="text-sm text-gray-500">{t.description}</div>}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (context === undefined) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

export default useToast;