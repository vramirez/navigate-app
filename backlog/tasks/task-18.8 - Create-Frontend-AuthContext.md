---
id: task-18.8
title: 'Create Frontend AuthContext with Business Type'
status: To Do
assignee:
  - '@claude'
created_date: '2025-10-28 16:30'
labels:
  - frontend
  - react
dependencies: [task-18.4]
parent: task-18
priority: high
estimated_hours: 3
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create React Context for authentication that fetches and stores user profile including business type. Provides useAuth hook for components to access current user's business type code for filtering articles.
<!-- SECTION:DESCRIPTION:END -->

## Implementation

**File**: `frontend/src/contexts/AuthContext.jsx` (NEW)

```jsx
import { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [business, setBusiness] = useState(null);
  const [businessTypeCode, setBusinessTypeCode] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Load user profile on mount
    loadUserProfile();
  }, []);

  const loadUserProfile = async () => {
    try {
      setLoading(true);
      setError(null);

      // Check if user is authenticated (token exists)
      const token = localStorage.getItem('authToken');
      if (!token) {
        setLoading(false);
        return;
      }

      // Fetch user profile from backend
      const response = await api.get('/businesses/auth/profile/');
      const data = response.data;

      setUser(data.user);
      setBusiness(data.business);
      setBusinessTypeCode(data.business_type_code);

    } catch (err) {
      console.error('Failed to load user profile:', err);
      setError(err.message);

      // If 401, clear token
      if (err.response?.status === 401) {
        localStorage.removeItem('authToken');
      }
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      setError(null);

      // Call login endpoint (adjust based on your auth system)
      const response = await api.post('/auth/login/', { username, password });
      const { token } = response.data;

      // Store token
      localStorage.setItem('authToken', token);

      // Load user profile
      await loadUserProfile();

      return { success: true };
    } catch (err) {
      console.error('Login failed:', err);
      setError(err.response?.data?.message || 'Login failed');
      return { success: false, error: err.message };
    }
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    setUser(null);
    setBusiness(null);
    setBusinessTypeCode(null);
  };

  const value = {
    // State
    user,
    business,
    businessTypeCode,
    loading,
    error,

    // Computed
    isAuthenticated: !!user,
    hasBusiness: !!business,

    // Methods
    login,
    logout,
    reload: loadUserProfile
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook for consuming auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

**File**: `frontend/src/main.jsx`

Wrap App with AuthProvider:
```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { AuthProvider } from './contexts/AuthContext'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>,
)
```

**File**: `frontend/src/services/api.js`

Update to include auth token:
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

## Testing

### Test 1: Context Provider

Create test file: `frontend/src/contexts/AuthContext.test.jsx`
```jsx
import { renderHook, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from './AuthContext';

describe('AuthContext', () => {
  it('provides auth context', () => {
    const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;

    const { result } = renderHook(() => useAuth(), { wrapper });

    expect(result.current).toHaveProperty('user');
    expect(result.current).toHaveProperty('businessTypeCode');
    expect(result.current).toHaveProperty('login');
    expect(result.current).toHaveProperty('logout');
  });

  it('throws error when used outside provider', () => {
    expect(() => {
      renderHook(() => useAuth());
    }).toThrow('useAuth must be used within AuthProvider');
  });
});
```

### Test 2: Manual Integration Test

Create test page: `frontend/src/pages/AuthTest.jsx`
```jsx
import { useAuth } from '../contexts/AuthContext';

export default function AuthTest() {
  const { user, business, businessTypeCode, loading, isAuthenticated } = useAuth();

  if (loading) return <div>Loading...</div>;

  return (
    <div style={{ padding: '20px' }}>
      <h1>Auth Context Test</h1>

      <section>
        <h2>Authentication Status</h2>
        <p>Is Authenticated: {isAuthenticated ? 'Yes' : 'No'}</p>
      </section>

      {user && (
        <section>
          <h2>User Info</h2>
          <pre>{JSON.stringify(user, null, 2)}</pre>
        </section>
      )}

      {business && (
        <section>
          <h2>Business Info</h2>
          <pre>{JSON.stringify(business, null, 2)}</pre>
          <p><strong>Business Type Code: {businessTypeCode}</strong></p>
        </section>
      )}
    </div>
  );
}
```

Add route to test:
```jsx
// In App.jsx
import AuthTest from './pages/AuthTest';

// Add route
<Route path="/auth-test" element={<AuthTest />} />
```

Visit http://localhost:3001/auth-test to verify.

### Test 3: Console Test

Open browser console on any page:
```javascript
// In browser console
window.__authContext = useAuth(); // Make available globally

// Check values
console.log('User:', __authContext.user);
console.log('Business Type:', __authContext.businessTypeCode);
```

## Acceptance Criteria

- [ ] AuthContext provides user, business, businessTypeCode
- [ ] Context loads profile automatically on mount
- [ ] useAuth hook accessible in all components
- [ ] Loading state handled properly
- [ ] Error state handled properly
- [ ] Login/logout methods work
- [ ] Token stored in localStorage
- [ ] 401 responses clear token and redirect
- [ ] API requests include Authorization header
- [ ] Context wraps entire app in main.jsx

## Notes

- Requires task-18.4 (profile endpoint) to be complete
- Token authentication system must be in place
- Future: Add token refresh logic
- Future: Persist business type selection if user has multiple businesses
