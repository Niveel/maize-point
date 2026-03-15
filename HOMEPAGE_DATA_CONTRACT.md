# Homepage Backend Data Contract

Last updated: 2026-03-15
Status: Implemented

## Scope
This contract covers homepage flow only:
- Navbar auth-aware state
- Hero section
- Benefits/highlights
- Product & price preview
- Testimonials
- Announcements/blog preview
- Footer contact info

---

## 1) Homepage User State (Navbar)

### Endpoint
- `GET /api/auth/me/`
- Equivalent: `GET /api/auth/profile/`

### Response shape
```json
{
  "id": 1,
  "username": "john_doe",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "user_type": "CUSTOMER",
  "profile_picture": "http://localhost:8000/media/profile_pictures/avatar.jpg",
  "is_verified": false,
  "is_active": true
}
```

Notes:
- Actual payload includes additional fields: `full_name`, `mobile_number`, `whatsapp_number`, `created_at`, `updated_at`.

### Auth behavior
- Unauthenticated: `401 Unauthorized`
- Strategy: JWT Bearer token via `Authorization: Bearer <access_token>`
- Cookie auth is not configured as default API auth.

---

## 2) Homepage Products Preview (Public)

### Endpoint
- `GET /api/home/products-preview/`

### Query params
- `featured=true|false` (supported; `featured=true` returns available products only)
- `limit=<number>` (supported; capped to 50)

### Response item shape
```json
{
  "id": 1,
  "slug": "yellow-maize",
  "name": "Yellow Maize",
  "description": "High quality yellow maize.",
  "maize_type": "Yellow Maize",
  "packaging_size": "50kg bag",
  "price_per_bag": "220.00",
  "price_per_ton": "4300.00",
  "currency": "GHS",
  "availability_status": "AVAILABLE",
  "image": null,
  "updated_at": "2026-03-15T18:11:09.000000Z"
}
```

### Availability enum values
- `AVAILABLE`
- `LOW_STOCK`
- `OUT_OF_STOCK`

### Type notes
- `price_per_bag` and `price_per_ton` are decimal strings.
- `image` currently resolves to `null` unless product image support is added later.

---

## 3) Homepage Announcements / Blog Preview

### Endpoint
- `GET /api/home/announcements-preview/`

### Query params
- `published=true|false` (default behavior returns published)
- `limit=<number>` (supported; capped to 50)

### Response item shape
```json
{
  "id": 3,
  "slug": "market-update-for-northern-region",
  "title": "Market Update for Northern Region",
  "excerpt": "Short summary text...",
  "cover_image": "http://localhost:8000/media/blog_images/update.jpg",
  "published_at": "2026-03-10T08:00:00.000000Z",
  "is_published": true
}
```

### Behavior
- Sort order: latest first (`-published_at`, `-created_at`).
- `excerpt` is backend-provided (derived from `content`).

---

## 4) Homepage Testimonials

### Endpoint
- `GET /api/home/testimonials/`

### Query params
- `is_featured=true|false` (optional)

### Response item shape
```json
{
  "id": 1,
  "customer_name": "Ama Mensah",
  "role_or_business": "Retail Buyer",
  "quote": "Reliable maize quality and timely delivery.",
  "is_featured": true,
  "created_at": "2026-03-10T09:30:00.000000Z"
}
```

### Publish controls
- Backend stores `is_published`; public endpoint returns only published testimonials.

---

## 5) Homepage Hero Metrics / Highlights

### Endpoint
- `GET /api/home/hero-metrics/`

### Response shape
```json
{
  "partner_farmers_count": 450,
  "avg_delivery_window": "24-48 hours",
  "repeat_customer_rate": "87.50",
  "last_updated": "2026-03-15T19:00:00.000000Z"
}
```

---

## 6) Homepage Benefits / How-It-Works Content

### Endpoint
- `GET /api/home/benefits/`

### Response shape
```json
[
  {
    "title": "Why Choose Us",
    "description": "What makes our supply model dependable.",
    "items": [
      {
        "title": "Consistent Quality",
        "description": "Batch-checked maize quality.",
        "display_order": 1
      },
      {
        "title": "Fast Dispatch",
        "description": "Quick turnaround after confirmation.",
        "display_order": 2
      }
    ]
  }
]
```

---

## 7) Footer Contact Info (Homepage)

### Endpoint
- `GET /api/home/footer-contact/`

### Response shape
```json
{
  "phone": "+233000000000",
  "whatsapp": "+233000000000",
  "email": "support@maizepoint.com",
  "office_location_text": "Tamale, Ghana",
  "office_map_url": "https://maps.google.com/..."
}
```

---

## 8) Common API Response Format

### Current standard
- No global `success/message/data` envelope is used.
- Success responses return raw object/list/paginated payloads.

### Error format
Examples:
```json
{
  "detail": "Authentication credentials were not provided."
}
```
```json
{
  "field_name": ["Error message"]
}
```

---

## 9) Pagination Format

Global pagination (DRF `PageNumberPagination`) applies to list endpoints by default:

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/products/?page=2",
  "previous": null,
  "results": []
}
```

Note:
- Homepage preview endpoints that accept `limit` return direct arrays for contract simplicity.

---

## 10) Endpoint List Needed by Frontend

1. Navbar state (auth):
- `GET /api/auth/me/`

2. Products preview:
- `GET /api/home/products-preview/?featured=true&limit=3`

3. Announcements preview:
- `GET /api/home/announcements-preview/?published=true&limit=3`

4. Testimonials:
- `GET /api/home/testimonials/?is_featured=true`

5. Hero metrics:
- `GET /api/home/hero-metrics/`

6. Benefits content:
- `GET /api/home/benefits/`

7. Footer contact:
- `GET /api/home/footer-contact/`

---

## Backend Notes

- New homepage data models are admin-manageable:
  - `HeroMetric`
  - `BenefitSection` + `BenefitItem`
  - `Testimonial`
  - `FooterContact`
- Migration added: `homepage/migrations/0001_initial.py`
