---
id: task-19
title: 'Fix Login Authentication System'
status: To Do
assignee:
  - '@claude'
created_date: '2025-10-30'
labels:
  - frontend
  - backend
  - authentication
  - bug
priority: high
estimated_hours: 2
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The login system is not properly implemented. The frontend has a mock login that doesn't call the backend API, and the backend login endpoint has CSRF configuration issues preventing authentication from the frontend.
<!-- SECTION:DESCRIPTION:END -->

## Current Issues

1. **Frontend Login.jsx is a mock** - Only logs to console, doesn't actually authenticate
   - File: `frontend/src/pages/Login.jsx`
   - Line 14: `// Mock login - in real app, this would authenticate with backend`

2. **Backend login endpoint has CSRF issues**
   - File: `backend/businesses/auth_views.py` (created but not working)
   - Returns 403 Forbidden due to CSRF cookie not set
   - `csrf_exempt` decorator not being applied correctly

3. **Missing authApi service in frontend**
   - No centralized API service for authentication calls
   - Need to create: `frontend/src/services/authApi.js`

## Implementation Plan

### Backend

**1. Fix CSRF configuration for login endpoint**
- Ensure `rest_framework.authtoken` is in INSTALLED_APPS ✓ (already added)
- Properly apply `csrf_exempt` to login view
- Test with curl to verify 200 response

**2. Verify auth endpoints work**
```bash
# Login should return token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "pubowner", "password": "test123"}'

# Should return: {"token": "...", "user_id": 1, "username": "pubowner"}

# Logout should delete token
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Token <token>"
```

### Frontend

**3. Create authApi service**

File: `frontend/src/services/authApi.js`

```javascript
import apiClient from './api'

export const login = async (username, password) => {
  try {
    const response = await apiClient.post('/api/auth/login/', {
      username,
      password,
    })
    return response.data
  } catch (error) {
    console.error('Login error:', error)
    throw error
  }
}

export const logout = async () => {
  try {
    await apiClient.post('/api/auth/logout/')
  } catch (error) {
    console.error('Logout error:', error)
    throw error
  }
}

export default {
  login,
  logout,
}
```

**4. Update Login.jsx to use real authentication**

Replace mock implementation with:

```javascript
import { login } from '../services/authApi'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'

// In Login component:
const { login: authLogin } = useAuth()
const navigate = useNavigate()
const [error, setError] = useState('')
const [loading, setLoading] = useState(false)

const handleSubmit = async (e) => {
  e.preventDefault()
  setError('')
  setLoading(true)

  try {
    const data = await login(email, password) // email is actually username
    await authLogin(data.token)
    navigate('/dashboard')
  } catch (err) {
    setError(err.response?.data?.error || 'Login failed')
  } finally {
    setLoading(false)
  }
}
```

**5. Add logout functionality to header/navigation**

Update header component to include logout button that calls:
```javascript
const { logout } = useAuth()
const navigate = useNavigate()

const handleLogout = async () => {
  await logout()
  navigate('/login')
}
```

## Testing

### Test 1: Backend Login Endpoint
```bash
# Should return token (200 OK)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "pubowner", "password": "test123"}'
```

### Test 2: Frontend Login Flow
1. Go to http://localhost:3001/login
2. Enter credentials: `pubowner` / `test123`
3. Should redirect to dashboard
4. Should see 4 articles (pub-specific)
5. Should see logout button in header

### Test 3: Logout Flow
1. Click logout button
2. Should clear token from localStorage
3. Should redirect to login page
4. Should not be able to access dashboard without logging in

### Test 4: Token Persistence
1. Login successfully
2. Close browser
3. Open browser again
4. Navigate to http://localhost:3001
5. Should still be logged in (token persists)

## Acceptance Criteria

- [ ] Backend login endpoint returns 200 with valid token
- [ ] Backend logout endpoint deletes token successfully
- [ ] Frontend Login.jsx calls real API (not mock)
- [ ] Frontend authApi service created
- [ ] Login redirects to dashboard on success
- [ ] Error messages display for invalid credentials
- [ ] Logout button visible when authenticated
- [ ] Logout clears token and redirects to login
- [ ] Token persists in localStorage across page refreshes
- [ ] AuthContext loads user profile on mount
- [ ] Protected routes redirect to login if not authenticated
- [ ] No CSRF errors in console or network tab

## Workaround (Temporary)

Until this is fixed, users can manually set token in browser console:

```javascript
// Get token for test users:
// pubowner: 073d6daffce118465588be605e82617941443b52

localStorage.setItem("auth_token", "073d6daffce118465588be605e82617941443b52")
window.location.reload()
```

## Files to Modify

**Backend:**
- `backend/businesses/auth_views.py` - Fix CSRF exemption
- `backend/navigate/settings.py` - Verify authtoken in INSTALLED_APPS ✓
- `backend/navigate/urls.py` - Verify csrf_exempt wrapper applied

**Frontend:**
- `frontend/src/services/authApi.js` - Create new file
- `frontend/src/pages/Login.jsx` - Replace mock with real auth
- `frontend/src/components/Header.jsx` or navigation - Add logout button
- `frontend/src/contexts/AuthContext.jsx` - Verify login/logout methods work

## Notes

- CSRF exemption needed for login endpoint (public endpoint, no prior auth)
- Token authentication doesn't require CSRF for API calls (uses Authorization header)
- Consider adding "Remember Me" functionality later
- Consider adding password reset flow later
- Test with all 4 business type test accounts
