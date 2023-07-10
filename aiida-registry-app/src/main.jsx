import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom';
import App from './App.jsx'
const currentPath = import.meta.env.VITE_BASE_PATH || "/aiida-registry/";
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter basename={currentPath}>
    <App />
    </BrowserRouter>
  </React.StrictMode>
)
