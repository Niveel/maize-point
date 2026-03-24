# Frontend Auth Guide (Complete)

As of March 24, 2026, this backend exposes the auth endpoints below under `/api/auth/`.

## Base URL
- Local API base: `http://127.0.0.1:8000/api`
- Auth base: `http://127.0.0.1:8000/api/auth`
- Typical frontend local origins allowed: `http://localhost:3000`, `http://localhost:3001`, `http://localhost:5173`

## Endpoint Summary
| Endpoint | Method | Auth Required | Purpose |
|---|---|---|---|
| `/auth/register/` | `POST` | No | Create a new customer account and return JWT tokens |
| `/auth/login/` | `POST` | No | Login with username or email and return JWT tokens |
| `/auth/refresh/` | `POST` | No | Exchange refresh token for new access token (and maybe new refresh token) |
| `/auth/logout/` | `POST` | Yes | Blacklist refresh token and log user out |
| `/auth/me/` | `GET`, `PUT`, `PATCH` | Yes | Read or update current user profile |
| `/auth/profile/` | `GET`, `PUT`, `PATCH` | Yes | Alias of `/auth/me/` (same behavior) |
| `/auth/profile-picture/` | `PATCH` | Yes | Upload/update profile picture via `multipart/form-data` |
| `/auth/change-password/` | `POST` | Yes | Change password for logged-in user |
| `/auth/notification-preferences/` | `GET`, `PATCH`, `PUT` | Yes | Read/update notification preferences |

## Important: Forgot Password / Reset Password
There is currently no forgot-password endpoint in this backend.

Missing routes:
- `POST /auth/forgot-password/`
- `POST /auth/reset-password/`

Frontend implication:
- Hide or disable "Forgot password" flow until backend endpoints are added.
- If you show the UI, wire it to a "Contact support" fallback for now.

## JWT Token Rules
- Use `Authorization: Bearer <access_token>` on protected endpoints.
- Refresh token rotation is enabled (`ROTATE_REFRESH_TOKENS=True`).
- Refresh token blacklisting is enabled (`BLACKLIST_AFTER_ROTATION=True`).
- Always replace stored refresh token when `/auth/refresh/` returns a new one.

## 1) Register
Endpoint: `POST /api/auth/register/`

Request body:
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "StrongPass123!",
  "password2": "StrongPass123!",
  "first_name": "John",
  "last_name": "Doe",
  "mobile_number": "+233241234567",
  "whatsapp_number": "+233241234567"
}
```

Validation notes:
- `password` and `password2` must match.
- `mobile_number` must start with `+233`.
- User type is forced to `CUSTOMER` by backend.

Success (`201 Created`):
```json
{
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "user_type": "CUSTOMER",
    "profile_picture": null,
    "mobile_number": "+233241234567",
    "whatsapp_number": "+233241234567",
    "is_verified": false,
    "is_active": true,
    "created_at": "2026-03-24T10:00:00Z",
    "updated_at": "2026-03-24T10:00:00Z"
  },
  "tokens": {
    "refresh": "<refresh_token>",
    "access": "<access_token>"
  },
  "message": "Registration successful. Please check your email for verification."
}
```

## 2) Login
Endpoint: `POST /api/auth/login/`

You can login with either `username` or `email`.

Request (username):
```json
{
  "username": "john_doe",
  "password": "StrongPass123!"
}
```

Request (email):
```json
{
  "email": "john@example.com",
  "password": "StrongPass123!"
}
```

Success (`200 OK`):
```json
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```

## 3) Refresh Token
Endpoint: `POST /api/auth/refresh/`

Request:
```json
{
  "refresh": "<refresh_token>"
}
```

Success (`200 OK`):
```json
{
  "access": "<new_access_token>",
  "refresh": "<new_refresh_token_if_rotated>"
}
```

Frontend behavior:
- Always update saved access token.
- If response includes `refresh`, replace stored refresh token too.
- If refresh fails (401/403), clear auth state and redirect to login.

## 4) Logout
Endpoint: `POST /api/auth/logout/`

Headers:
- `Authorization: Bearer <access_token>`

Body:
```json
{
  "refresh_token": "<refresh_token>"
}
```

Success (`205 Reset Content`):
```json
{
  "message": "Logout successful."
}
```

Notes:
- If you omit `refresh_token`, backend still returns success but will not blacklist anything.
- Best practice is always to send it.

## 5) Current User Profile (`/me/` and `/profile/`)
Endpoint:
- `GET /api/auth/me/`
- `PATCH /api/auth/me/`
- `PUT /api/auth/me/`
- `GET/PATCH/PUT /api/auth/profile/` (alias)

Headers:
- `Authorization: Bearer <access_token>`

Read response (`200 OK`):
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "username": "john_doe",
  "email": "john@example.com",
  "mobile_number": "+233241234567",
  "whatsapp_number": "+233241234567",
  "location": "Accra",
  "profile_picture": "/media/profile_pictures/avatar.jpg",
  "profile_picture_url": "http://127.0.0.1:8000/media/profile_pictures/avatar.jpg",
  "is_verified": false,
  "is_active": true,
  "user_type": "CUSTOMER"
}
```

Update payload (`PATCH` recommended):
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "username": "john_doe_updated",
  "email": "john.new@example.com",
  "mobile_number": "+233241234568",
  "whatsapp_number": "+233241234568",
  "location": "Kumasi"
}
```

Validation notes:
- `username` must be unique.
- `mobile_number` must be unique.
- `location` is mapped into customer profile data.

## 6) Profile Picture Upload
Endpoint: `PATCH /api/auth/profile-picture/`

Headers:
- `Authorization: Bearer <access_token>`
- `Content-Type: multipart/form-data`

Form data:
- `profile_picture`: image file

Success (`200 OK`): returns the same full profile contract as `/auth/me/`.

## 7) Change Password
Endpoint: `POST /api/auth/change-password/`

Headers:
- `Authorization: Bearer <access_token>`

Supported request keys:
- `current_password` or `old_password`
- `new_password`
- `confirm_new_password` or `new_password2`

Recommended payload:
```json
{
  "current_password": "OldPass123!",
  "new_password": "NewStrongPass456!",
  "confirm_new_password": "NewStrongPass456!"
}
```

Success (`200 OK`):
```json
{
  "message": "Password changed successfully."
}
```

## 8) Notification Preferences
Endpoint:
- `GET /api/auth/notification-preferences/`
- `PATCH /api/auth/notification-preferences/`
- `PUT /api/auth/notification-preferences/`

Headers:
- `Authorization: Bearer <access_token>`

Read response (`200 OK`):
```json
{
  "order_updates": true,
  "price_alerts": true,
  "announcements": true,
  "whatsapp_notifications": false,
  "updated_at": "2026-03-24T10:00:00Z"
}
```

Update payload example:
```json
{
  "order_updates": true,
  "price_alerts": false,
  "announcements": true,
  "whatsapp_notifications": true
}
```

## Standard Error Shape
This API uses a custom error handler. Most errors come in this format:

```json
{
  "message": "Validation failed.",
  "errors": {
    "field_name": ["Error message"]
  }
}
```

Auth/permission examples:
```json
{
  "message": "Authentication failed.",
  "errors": {
    "auth": ["Authentication credentials were not provided."]
  }
}
```

## Frontend Token Strategy (Recommended)
1. On login/register, save `access` + `refresh`.
2. Attach `Authorization: Bearer <access>` for protected requests.
3. On first `401`, call `/auth/refresh/` once.
4. Retry the failed request once with new access token.
5. If refresh fails, clear tokens and redirect to login.
6. On logout, call `/auth/logout/` with refresh token, then clear local tokens.

## TypeScript Client Snippet
```ts
const API_BASE = "http://127.0.0.1:8000/api";

type Tokens = { access?: string; refresh?: string };

const tokenStore = {
  get(): Tokens {
    return {
      access: localStorage.getItem("access") || undefined,
      refresh: localStorage.getItem("refresh") || undefined,
    };
  },
  set(tokens: Tokens) {
    if (tokens.access) localStorage.setItem("access", tokens.access);
    if (tokens.refresh) localStorage.setItem("refresh", tokens.refresh);
  },
  clear() {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
  },
};

async function refreshAccessToken(): Promise<string> {
  const { refresh } = tokenStore.get();
  if (!refresh) throw new Error("No refresh token");

  const res = await fetch(`${API_BASE}/auth/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });

  const data = await res.json();
  if (!res.ok) {
    tokenStore.clear();
    throw data;
  }

  tokenStore.set({ access: data.access, refresh: data.refresh });
  return data.access;
}

export async function authFetch(path: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers || {});
  const { access } = tokenStore.get();

  if (!headers.has("Content-Type") && !(init.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (access) headers.set("Authorization", `Bearer ${access}`);

  let res = await fetch(`${API_BASE}${path}`, { ...init, headers });

  if (res.status === 401) {
    const newAccess = await refreshAccessToken();
    headers.set("Authorization", `Bearer ${newAccess}`);
    res = await fetch(`${API_BASE}${path}`, { ...init, headers });
  }

  return res;
}
```

## Quick Frontend Checklist
- Use `/auth/login/` with `username` or `email`.
- Implement refresh-token retry logic globally (interceptor/wrapper).
- Treat `/auth/me/` as session bootstrap endpoint.
- Use `multipart/form-data` for `/auth/profile-picture/`.
- Do not ship forgot-password UI as active unless backend endpoints are added.
