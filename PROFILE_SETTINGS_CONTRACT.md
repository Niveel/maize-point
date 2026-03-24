# Profile & Preferences Backend Contract

## Base
- API base: `http://127.0.0.1:8000/api`
- All endpoints below require auth:
```http
Authorization: Bearer <access_token>
```

## 1) Profile Read Contract

### Endpoint
- `GET /api/auth/profile/`
- Alias: `GET /api/auth/me/`

### Response (`200`)
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

Notes:
- `location` is sourced from the customer profile.
- For users without customer profile, `location` may be `null`.

## 2) Profile Update Contract

### Endpoint
- `PATCH /api/auth/profile/` (recommended partial update)
- `PUT /api/auth/profile/` (full replacement style)

### Editable fields
- `first_name`
- `last_name`
- `username`
- `email`
- `mobile_number`
- `whatsapp_number`
- `location`
- `profile_picture` (also supported here via multipart)

### JSON update example
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

### Success response (`200`)
- Returns the same full profile object as profile read contract.

## 3) Password Change Contract

### Endpoint
- `POST /api/auth/change-password/`

### Request payload (preferred)
```json
{
  "current_password": "OldPass123!",
  "new_password": "NewStrongPass123!",
  "confirm_new_password": "NewStrongPass123!"
}
```

Backward-compatible fields also accepted:
- `old_password` instead of `current_password`
- `new_password2` instead of `confirm_new_password`

### Success response (`200`)
```json
{
  "message": "Password changed successfully."
}
```

## 4) Notification Preferences Contract

### Read preferences
- `GET /api/auth/notification-preferences/`

Response (`200`)
```json
{
  "order_updates": true,
  "price_alerts": true,
  "announcements": true,
  "whatsapp_notifications": false,
  "updated_at": "2026-03-20T16:00:00.000000Z"
}
```

### Update preferences
- `PATCH /api/auth/notification-preferences/` (recommended)
- `PUT /api/auth/notification-preferences/`

Update payload:
```json
{
  "order_updates": true,
  "price_alerts": false,
  "announcements": true,
  "whatsapp_notifications": true
}
```

Response (`200`): same shape as read.

## 5) Profile Picture Contract

### Endpoint (dedicated)
- `PATCH /api/auth/profile-picture/`

### Request format
- `multipart/form-data`
- Field name: `profile_picture`

Example (curl):
```bash
curl -X PATCH "http://127.0.0.1:8000/api/auth/profile-picture/" \
  -H "Authorization: Bearer <access_token>" \
  -F "profile_picture=@/path/to/photo.jpg"
```

### Response (`200`)
- Returns full profile object including:
  - `profile_picture` (relative media path)
  - `profile_picture_url` (absolute URL)

## 6) Consistent Error/Validation Shape

The API now uses a unified error contract:

### Validation errors (`400`)
```json
{
  "message": "Validation failed.",
  "errors": {
    "field_name": ["Error message"],
    "non_field_errors": ["General validation error"]
  }
}
```

Password examples:
- Wrong current password:
```json
{
  "message": "Validation failed.",
  "errors": {
    "current_password": ["Current password is incorrect."]
  }
}
```
- Password mismatch:
```json
{
  "message": "Validation failed.",
  "errors": {
    "confirm_new_password": ["New password fields didn't match."]
  }
}
```
- Weak password (Django validators):
```json
{
  "message": "Validation failed.",
  "errors": {
    "new_password": ["This password is too common."]
  }
}
```

### Auth errors (`401`)
```json
{
  "message": "Authentication failed.",
  "errors": {
    "auth": ["Authentication credentials were not provided."]
  }
}
```

### Permission errors (`403`)
```json
{
  "message": "Permission denied.",
  "errors": {
    "permission": ["You do not have permission to perform this action."]
  }
}
```

