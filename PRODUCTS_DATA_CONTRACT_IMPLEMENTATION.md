# Products Data Contract Implementation

Last updated: 2026-03-15
Status: Implemented

## Implemented Endpoints

1. Primary products list:
- `GET /api/products/`

2. Categories list:
- `GET /api/product-categories/`

---

## 1) Query Params Supported on `/api/products/`

- `q`: search over `name`, `maize_type`, `description`, `category.name`
- `category`: category slug or category name
- `availability`: `AVAILABLE | LOW_STOCK | OUT_OF_STOCK`
- `sort`:
  - `featured`
  - `price_asc`
  - `price_desc`
  - `name_asc`
  - `name_desc`
- `page`: 1-based page number
- `page_size`: `1..100` (supports `4`, `6`, `12`)

Example:
`GET /api/products/?q=yellow&category=yellow&availability=AVAILABLE&sort=price_asc&page=2&page_size=6`

---

## 2) Response Shape (`/api/products/`)

Paginated response:

```json
{
  "count": 124,
  "next": "http://localhost:8000/api/products/?page=3&page_size=6&sort=price_asc",
  "previous": "http://localhost:8000/api/products/?page=1&page_size=6&sort=price_asc",
  "results": [
    {
      "id": 1,
      "slug": "premium-yellow-maize",
      "name": "Premium Yellow Maize",
      "category": {
        "id": "yellow",
        "name": "Yellow Maize"
      },
      "maize_type": "Yellow Maize",
      "description": "Clean sorted kernels for feed operations.",
      "packaging_size": "50kg bag",
      "price_per_bag": "420.00",
      "price_per_ton": "7950.00",
      "currency": "GHS",
      "availability_status": "AVAILABLE",
      "min_order_quantity": "5 bags",
      "image_url": "http://localhost:8000/media/products/premium-yellow.jpg",
      "updated_at": "2026-03-15T18:11:09.000000Z"
    }
  ]
}
```

Notes:
- Prices are returned as string decimals.
- `image_url` is absolute when image exists; `null` if unavailable.
- Category may be `null` if product has no category assigned.

---

## 3) Image Requirement

Implemented:
- Product model now includes:
  - `image = models.ImageField(upload_to="products/", null=True, blank=True)`
- Product admin supports image upload/edit.
- API returns `image_url` as absolute URL when present.

---

## 4) Categories Endpoint

Endpoint:
- `GET /api/product-categories/`

Response shape:

```json
[
  {
    "id": "yellow",
    "name": "Yellow Maize",
    "description": "Best suited for feed mills.",
    "product_count": 42
  }
]
```

---

## 5) Performance + UX

Implemented:
- Stable ordering includes deterministic fallback (`id`).
- Added product indexes:
  - `name`
  - `slug`
  - `maize_type`
  - `availability_status`
  - `category`
  - `is_available` (compatibility field)
- Added pricing index:
  - `(product, is_current, price_per_ton)` for price-based sorting support.

---

## 6) Error Contract

Implemented:

Invalid availability:
```json
{
  "detail": "Invalid availability value."
}
```

Query validation example:
```json
{
  "errors": {
    "page_size": ["Must be between 1 and 100"]
  }
}
```

---

## 7) Final Backend Decisions

1. `availability_status` enum values:
- `AVAILABLE`
- `LOW_STOCK`
- `OUT_OF_STOCK`

2. Prices:
- Returned as string decimals (`"420.00"`).

3. Maximum `page_size`:
- `100`

4. Supported `sort` values:
- `featured`, `price_asc`, `price_desc`, `name_asc`, `name_desc`

5. Search fields for `q`:
- `name`, `maize_type`, `description`, `category.name`

---

## 8) Files Changed

- `products/models.py`
- `products/serializers.py`
- `products/views.py`
- `products/admin.py`
- `products/migrations/0002_alter_product_options_product_availability_status_and_more.py`
- `pricing/models.py`
- `pricing/migrations/0002_price_prices_product_86ea6b_idx.py`
- `maize_point/urls.py`

---

## Verification Run

Commands executed:
- `python manage.py makemigrations products pricing`
- `python manage.py migrate`
- `python manage.py check`

Quick endpoint checks:
- `GET /api/products/?page_size=6&sort=name_asc` -> `200`
- `GET /api/product-categories/` -> `200`
- `GET /api/products/?availability=BAD` -> `400` with `detail`
