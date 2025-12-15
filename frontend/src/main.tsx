import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './index.css'
import App from './App.tsx'
import { authApi } from './api/auth'

// Global error handler to catch startup issues
window.onerror = function (message, source, lineno, colno, error) {
  const root = document.getElementById('root');
  if (root) {
    root.innerHTML = `<div style="color: red; padding: 20px;">
            <h1>Startup Error</h1>
            <pre>${message}\nAt: ${source}:${lineno}:${colno}</pre>
        </div>`;
  }
  console.error("Global Error:", message, error);
};

const queryClient = new QueryClient()

const initApp = async () => {
  console.log("App starting...");
  const root = createRoot(document.getElementById('root')!);

  // Show loading state immediately
  root.render(<div style={{ padding: 20 }}>Loading application...</div>);

  try {
    console.log("Fetching CSRF token...");
    await authApi.getCsrf();
    console.log("CSRF token fetched successfully.");
  } catch (e) {
    console.error("Failed to initialize CSRF", e);
  }

  console.log("Rendering React App...");
  root.render(
    <StrictMode>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </QueryClientProvider>
    </StrictMode>,
  )
};

initApp().catch(e => {
  console.error("Init App Failed", e);
  const root = document.getElementById('root');
  if (root) root.innerHTML = `<div style="color:red">App Init Failed: ${e}</div>`;
});
