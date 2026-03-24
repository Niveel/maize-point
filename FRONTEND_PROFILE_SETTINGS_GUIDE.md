# Frontend Guide: Profile Settings

## Base Setup
- API base: `http://127.0.0.1:8000/api`
- Auth header:
```http
Authorization: Bearer <access_token>
```

## Endpoints You Will Use
- `GET /api/auth/profile/` (or `/api/auth/me/`) -> load profile settings
- `PATCH /api/auth/profile/` -> update editable profile fields
- `POST /api/auth/change-password/` -> change password
- `GET /api/auth/notification-preferences/` -> load notification toggles
- `PATCH /api/auth/notification-preferences/` -> update notification toggles
- `PATCH /api/auth/profile-picture/` -> upload profile image (multipart/form-data)

---

## 1) Load Profile (Settings Page)

### Request
`GET /api/auth/profile/`

### Response shape
```json
{
  "id": 21,
  "first_name": "John",
  "last_name": "Doe",
  "username": "john_doe",
  "email": "john@example.com",
  "mobile_number": "+233241234567",
  "whatsapp_number": "+233241234567",
  "location": "Accra",
  "profile_picture": "/media/profile_pictures/john.jpg",
  "profile_picture_url": "http://127.0.0.1:8000/media/profile_pictures/john.jpg",
  "is_verified": false,
  "is_active": true,
  "user_type": "CUSTOMER"
}
```

---

## 2) Update Profile

### Request
`PATCH /api/auth/profile/`

### Editable payload
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "username": "john_doe_2",
  "email": "john2@example.com",
  "mobile_number": "+233241111111",
  "whatsapp_number": "+233242222222",
  "location": "Tema"
}
```

### Response
- Returns updated full profile object.

---

## 3) Change Password

### Request
`POST /api/auth/change-password/`

### Preferred payload
```json
{
  "current_password": "OldPass123!",
  "new_password": "NewStrongPass123!",
  "confirm_new_password": "NewStrongPass123!"
}
```

### Success response
```json
{
  "message": "Password changed successfully."
}
```

---

## 4) Notification Preferences

### Load
`GET /api/auth/notification-preferences/`

Response:
```json
{
  "order_updates": true,
  "price_alerts": true,
  "announcements": true,
  "whatsapp_notifications": false,
  "updated_at": "2026-03-20T16:00:00.000000Z"
}
```

### Update
`PATCH /api/auth/notification-preferences/`

Payload:
```json
{
  "order_updates": true,
  "price_alerts": false,
  "announcements": true,
  "whatsapp_notifications": true
}
```

---

## 5) Upload Profile Picture

### Request
`PATCH /api/auth/profile-picture/`

Use `multipart/form-data`:
- field name: `profile_picture`

Example with `fetch`:
```ts
const form = new FormData();
form.append("profile_picture", file);

await fetch(`${API_BASE}/auth/profile-picture/`, {
  method: "PATCH",
  headers: { Authorization: `Bearer ${accessToken}` },
  body: form,
});
```

---

## 6) Standard Error Contract (Frontend Mapping)

### Validation (`400`)
```json
{
  "message": "Validation failed.",
  "errors": {
    "field_name": ["Error message"],
    "non_field_errors": ["General validation error"]
  }
}
```

### Auth (`401`)
```json
{
  "message": "Authentication failed.",
  "errors": {
    "auth": ["Authentication credentials were not provided."]
  }
}
```

### Permission (`403`)
```json
{
  "message": "Permission denied.",
  "errors": {
    "permission": ["You do not have permission to perform this action."]
  }
}
```

Frontend tip:
- Always map errors from `errors[field]` to field inputs.
- Show first error text for each field.

---

## 7) Copy-Paste TypeScript Client

```ts
const API_BASE = "http://127.0.0.1:8000/api";

function authHeaders() {
  const access = localStorage.getItem("access");
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${access}`,
  };
}

async function toJson(res: Response) {
  const data = await res.json();
  if (!res.ok) throw data;
  return data;
}

export async function getProfile() {
  const res = await fetch(`${API_BASE}/auth/profile/`, {
    headers: authHeaders(),
  });
  return toJson(res);
}

export async function updateProfile(payload: Record<string, unknown>) {
  const res = await fetch(`${API_BASE}/auth/profile/`, {
    method: "PATCH",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  return toJson(res);
}

export async function changePassword(payload: {
  current_password: string;
  new_password: string;
  confirm_new_password: string;
}) {
  const res = await fetch(`${API_BASE}/auth/change-password/`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  return toJson(res);
}

export async function getNotificationPreferences() {
  const res = await fetch(`${API_BASE}/auth/notification-preferences/`, {
    headers: authHeaders(),
  });
  return toJson(res);
}

export async function updateNotificationPreferences(payload: {
  order_updates?: boolean;
  price_alerts?: boolean;
  announcements?: boolean;
  whatsapp_notifications?: boolean;
}) {
  const res = await fetch(`${API_BASE}/auth/notification-preferences/`, {
    method: "PATCH",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  return toJson(res);
}

export async function uploadProfilePicture(file: File) {
  const access = localStorage.getItem("access");
  const form = new FormData();
  form.append("profile_picture", file);

  const res = await fetch(`${API_BASE}/auth/profile-picture/`, {
    method: "PATCH",
    headers: { Authorization: `Bearer ${access}` },
    body: form,
  });
  return toJson(res);
}
```

