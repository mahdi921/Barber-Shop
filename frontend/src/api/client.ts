import axios from 'axios';

// Create a configured axios instance
// We use a relative URL so it works with the proxy in setup or production
const client = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '',
    withCredentials: true, // Important for session cookies
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
});

// Helper to get cookie by name (for CSRF token)
function getCookie(name: string): string | null {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Request interceptor to add CSRF token
client.interceptors.request.use(
    (config) => {
        // Only add CSRF token for mutating requests (POST, PUT, PATCH, DELETE)
        // GET/HEAD/OPTIONS/TRACE methods are safe and don't require CSRF validation
        const safeMethods = ['get', 'head', 'options', 'trace'];
        if (!safeMethods.includes(config.method?.toLowerCase() || '')) {
            const csrftoken = getCookie('csrftoken');
            if (csrftoken) {
                config.headers['X-CSRFToken'] = csrftoken;
            }
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for global error handling (optional, e.g. 401 redirect)
client.interceptors.response.use(
    (response) => response,
    (error) => {
        // Handle 401 Unauthorized globally if needed (e.g. redirect to login)
        // but usually better to handle in React Query or Auth Context
        return Promise.reject(error);
    }
);

export default client;
