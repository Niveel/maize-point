# Dashboard Endpoint Guide

## One-Call Dashboard API

- Endpoint: `GET /api/home/dashboard/`
- Auth: required (`Bearer <access_token>`)
- Role-aware payload:
  - `ADMIN`/`STAFF`: business metrics + alerts + recent activity
  - `CUSTOMER`: personal metrics + profile + recent activity

Base URL:
- `http://127.0.0.1:8000/api`

Auth header:
```http
Authorization: Bearer <access_token>
```

---

## Admin/Staff Response

Example (`200`):
```json
{
  "role": "ADMIN",
  "generated_at": "2026-03-20T14:22:10.441028Z",
  "metrics": {
    "farmers": {
      "total_farmers": 124,
      "approved_farmers": 103,
      "active_farmers": 118,
      "supplies_summary": {
        "total_supplies": 15840,
        "total_cost": "2045000.00",
        "total_paid": "1720000.00"
      }
    },
    "orders": {
      "total_orders": 640,
      "pending_orders": 18,
      "processing_orders": 22,
      "dispatched_orders": 9,
      "delivered_orders": 571,
      "cancelled_orders": 20,
      "total_revenue": "5067800.00"
    },
    "inventory": {
      "total_bags": 29000,
      "total_tons": "1450.000",
      "low_stock_count": 7,
      "expiring_soon_count": 4
    }
  },
  "alerts": {
    "low_stock": [
      {
        "id": 12,
        "product": 3,
        "product_name": "Premium Yellow Maize",
        "quantity_bags": 42,
        "quantity_tons": "2.100",
        "source_type": "FARMER",
        "farmer": 18,
        "farmer_name": "Kwame Mensah",
        "quality_grade": "Grade A",
        "moisture_content": "13.20",
        "warehouse_location": "Main Warehouse",
        "cost_price": "260.00",
        "date_received": "2026-03-01T08:00:00Z",
        "expiry_alert_date": "2026-03-30",
        "notes": "",
        "is_low_stock": true,
        "created_at": "2026-03-01T08:01:00Z",
        "updated_at": "2026-03-20T10:15:21Z"
      }
    ],
    "expiring_soon": [
      {
        "id": 15,
        "product": 1,
        "product_name": "White Maize",
        "quantity_bags": 150,
        "quantity_tons": "7.500",
        "source_type": "FARMER",
        "farmer": 9,
        "farmer_name": "Ama Boateng",
        "quality_grade": "Standard",
        "moisture_content": "12.80",
        "warehouse_location": "Warehouse B",
        "cost_price": "245.00",
        "date_received": "2026-02-20T08:00:00Z",
        "expiry_alert_date": "2026-03-25",
        "notes": "",
        "is_low_stock": false,
        "created_at": "2026-02-20T08:01:00Z",
        "updated_at": "2026-03-19T10:15:21Z"
      }
    ]
  },
  "recent_activity": {
    "orders": [
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
    ],
    "stock_movements": [
      {
        "id": 91,
        "stock": 12,
        "stock_product_name": "Premium Yellow Maize",
        "movement_type": "DEDUCTION",
        "quantity_bags": 30,
        "quantity_tons": "1.800",
        "order": 57,
        "reason": "Order ORDA1B2C3D4E approved",
        "performed_by": 1,
        "performed_by_name": "Admin User",
        "created_at": "2026-03-20T10:15:21.021411Z"
      }
    ],
    "farmers": [
      {
        "id": 18,
        "profile_picture": null,
        "full_name": "Kwame Mensah",
        "mobile_number": "+233241234567",
        "ghana_card_number": "GHA-123456789-0",
        "gps_latitude": "5.603700",
        "gps_longitude": "-0.187000",
        "region": "Greater Accra",
        "district": "Accra Metropolitan",
        "community": "Adenta",
        "maize_types_supplied": ["Yellow Maize"],
        "notes": "",
        "is_approved": true,
        "is_active": true,
        "created_by": 1,
        "created_by_name": "Admin User",
        "created_at": "2026-03-12T10:00:00Z",
        "updated_at": "2026-03-15T09:00:00Z"
      }
    ]
  }
}
```

---

## Customer Response

Example (`200`):
```json
{
  "role": "CUSTOMER",
  "generated_at": "2026-03-20T14:22:10.441028Z",
  "metrics": {
    "orders": {
      "total_orders": 14,
      "pending_orders": 1,
      "processing_orders": 2,
      "dispatched_orders": 1,
      "delivered_orders": 10,
      "cancelled_orders": 0,
      "total_spent": "19850.00"
    },
    "hero": {
      "partner_farmers_count": 500,
      "avg_delivery_window": "24-48 hours",
      "repeat_customer_rate": "82.50",
      "last_updated": "2026-03-20T11:30:14.923182Z"
    }
  },
  "profile": {
    "id": 8,
    "user": {
      "id": 21,
      "username": "john_doe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "user_type": "CUSTOMER",
      "profile_picture": null,
      "mobile_number": "+233241234567",
      "whatsapp_number": null,
      "is_verified": false,
      "is_active": true,
      "created_at": "2026-03-18T09:31:00.000000Z",
      "updated_at": "2026-03-20T12:10:00.000000Z"
    },
    "customer_id": "CUS0008",
    "location": "Accra",
    "is_active": true,
    "total_orders": 14,
    "total_spent": "19850.00",
    "created_at": "2026-03-18T09:31:00.000000Z",
    "updated_at": "2026-03-20T12:10:00.000000Z"
  },
  "recent_activity": {
    "orders": [
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
  },
  "alerts": {}
}
```

---

## Notes

- This endpoint intentionally returns nested objects with serializer shapes already used by the existing API.
- `recent_activity` and alert lists are capped at `5` items each.
- If a customer profile does not exist, `profile` is `null` and customer metrics default to zero values.

---

## Error Responses

`401 Unauthorized`:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

`403 Forbidden` (invalid token/permission issues):
```json
{
  "detail": "You do not have permission to perform this action."
}
```
