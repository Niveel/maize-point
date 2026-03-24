# Frontend Guide: User Order History + Related Endpoints

## Base
- API base: `http://127.0.0.1:8000/api`
- Auth required for all order endpoints:
```http
Authorization: Bearer <access_token>
```

## Core Endpoint for User Order History

### `GET /api/orders/history/`
- Purpose: Get current logged-in customer's full order history.
- Auth: Customer JWT.
- Response type: array (not paginated).

Example response (`200`):
```json
[
  {
    "id": 57,
    "order_id": "ORDA1B2C3D4E",
    "customer": 8,
    "customer_details": { "...": "..." },
    "product": 3,
    "product_details": { "...": "..." },
    "quantity_bags": 20,
    "quantity_tons": "1.200",
    "unit_price": "350.00",
    "total_price": "7000.00",
    "delivery_method": "DELIVERY",
    "delivery_address": "Adenta, Accra",
    "delivery_date": "2026-03-22",
    "payment_option": "MOBILE_MONEY",
    "order_status": "PROCESSING",
    "customer_notes": "",
    "admin_notes": "",
    "approved_by": 1,
    "approved_by_name": "Admin User",
    "approved_at": "2026-03-20T10:15:21.001111Z",
    "created_at": "2026-03-20T09:58:00.000000Z",
    "updated_at": "2026-03-20T10:15:21.001111Z"
  }
]
```

---

## All Related Order Endpoints

### 1) `GET /api/orders/`
- Purpose: List orders.
- Customer sees only own orders.
- Admin/Staff sees all orders.
- Response: paginated (`count`, `next`, `previous`, `results`).

Query params:
- `order_status` (e.g. `PENDING`, `PROCESSING`, `DELIVERED`)
- `payment_option` (`CASH`, `BANK_TRANSFER`, `MOBILE_MONEY`)
- `delivery_method` (`PICKUP`, `DELIVERY`)
- `product` (product id)
- `search` (order id / customer name)
- `ordering` (`created_at`, `-created_at`, `total_price`, `-total_price`)
- `page`

Example:
- `GET /api/orders/?order_status=PROCESSING&ordering=-created_at&page=1`

### 2) `GET /api/orders/{id}/`
- Purpose: Order details page.
- Customer can fetch only own order.

### 3) `POST /api/orders/`
- Purpose: Create a new order (customer checkout).

Request body:
```json
{
  "product": 3,
  "quantity_bags": 20,
  "quantity_tons": "1.200",
  "unit_price": "350.00",
  "delivery_method": "DELIVERY",
  "delivery_address": "Adenta, Accra",
  "payment_option": "MOBILE_MONEY",
  "customer_notes": "Call before arrival"
}
```

Notes:
- If `delivery_method = DELIVERY`, `delivery_address` is required.
- `total_price` is calculated by backend.

### 4) `PATCH /api/orders/{id}/cancel/`
- Purpose: Cancel an order.
- Works unless order is already `DELIVERED` or `CANCELLED`.

Request body (optional):
```json
{
  "admin_notes": "Cancelled by customer request"
}
```

### 5) `PATCH /api/orders/{id}/approve/` (Admin/Staff)
- Purpose: Approve pending order and deduct stock (FIFO).
- No required body.

### 6) `PATCH /api/orders/{id}/update_status/` (Admin/Staff)
- Purpose: Update lifecycle state.

Request body:
```json
{
  "status": "DISPATCHED",
  "admin_notes": "Loaded and left warehouse"
}
```

Allowed statuses:
- `PENDING`
- `PROCESSING`
- `DISPATCHED`
- `DELIVERED`
- `CANCELLED`

### 7) `GET /api/home/dashboard/`
- Purpose: One-call dashboard endpoint.
- Customer response includes `recent_activity.orders`.
- Useful when order history is part of a dashboard screen.

---

## Frontend Integration Guide

## 1) API helpers (TypeScript)
```ts
const API_BASE = "http://127.0.0.1:8000/api";

function authHeaders() {
  const access = localStorage.getItem("access");
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${access}`,
  };
}

async function parseOrThrow(res: Response) {
  const data = await res.json();
  if (!res.ok) throw data;
  return data;
}

export async function getMyOrderHistory() {
  const res = await fetch(`${API_BASE}/orders/history/`, {
    method: "GET",
    headers: authHeaders(),
  });
  return parseOrThrow(res);
}

export async function getMyOrdersPage(params: {
  page?: number;
  order_status?: string;
  ordering?: string;
}) {
  const query = new URLSearchParams();
  if (params.page) query.set("page", String(params.page));
  if (params.order_status) query.set("order_status", params.order_status);
  if (params.ordering) query.set("ordering", params.ordering);

  const res = await fetch(`${API_BASE}/orders/?${query.toString()}`, {
    method: "GET",
    headers: authHeaders(),
  });
  return parseOrThrow(res);
}

export async function getOrderById(id: number) {
  const res = await fetch(`${API_BASE}/orders/${id}/`, {
    method: "GET",
    headers: authHeaders(),
  });
  return parseOrThrow(res);
}

export async function createOrder(payload: {
  product: number;
  quantity_bags: number;
  quantity_tons: string;
  unit_price: string;
  delivery_method: "PICKUP" | "DELIVERY";
  delivery_address?: string;
  payment_option: "CASH" | "BANK_TRANSFER" | "MOBILE_MONEY";
  customer_notes?: string;
}) {
  const res = await fetch(`${API_BASE}/orders/`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  return parseOrThrow(res);
}

export async function cancelOrder(id: number, admin_notes = "") {
  const res = await fetch(`${API_BASE}/orders/${id}/cancel/`, {
    method: "PATCH",
    headers: authHeaders(),
    body: JSON.stringify({ admin_notes }),
  });
  return parseOrThrow(res);
}
```

## 2) Suggested UI flow
1. Order History Page:
  - Use `getMyOrderHistory()` for a quick non-paginated history view.
2. Orders Table with filters:
  - Use `getMyOrdersPage()` for pagination + filter controls.
3. Order Details:
  - Open selected row and fetch `getOrderById(id)`.
4. Cancel action:
  - Show cancel button only for `PENDING|PROCESSING|DISPATCHED`.
  - Call `cancelOrder(id)` then refresh list.

## 3) Status badge map (frontend)
```ts
const statusColor: Record<string, string> = {
  PENDING: "gray",
  PROCESSING: "blue",
  DISPATCHED: "orange",
  DELIVERED: "green",
  CANCELLED: "red",
};
```

## 4) Common errors to handle
- `401`: expired token or missing auth header.
- `404`: order not found or no customer profile.
- `400`: invalid payload (e.g., missing delivery address for delivery order).
- `403`: non-admin user tried admin-only status update endpoint.

