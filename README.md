# Maize Supply & Storage Enterprise - Backend API

A comprehensive Django REST Framework backend for managing maize supply chain operations, including farmer management, inventory control, customer orders, and pricing.

## 🚀 Features

- **User Management**: Custom user system with Admin, Staff, and Customer roles
- **Farmer Management**: Track farmer information, supplies, and payments
- **Customer Management**: Handle customer profiles and order history
- **Product Management**: Manage maize products with multiple packaging sizes
- **Inventory Control**: Real-time stock tracking with alerts for low stock and expiring items
- **Order Management**: Complete order lifecycle from creation to delivery
- **Dynamic Pricing**: Maintain price history with current price tracking
- **Blog/CMS**: Content management for market insights and tips
- **Email Notifications**: Automated notifications for orders and registrations
- **Reports**: Comprehensive business analytics and reporting
- **API Documentation**: Auto-generated Swagger/ReDoc documentation

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 12+ (or SQLite for development)
- Redis (for Celery tasks)
- Virtual environment (recommended)

## 🛠️ Installation

### 1. Clone and Setup Virtual Environment

```powershell
cd c:\Users\eritt\Desktop\projects\maize_point
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy `.env.example` to `.env` and configure:

```powershell
copy .env.example .env
```

Edit `.env` file with your settings:
- Database credentials
- Email settings (Gmail/SMTP)
- Secret key
- CORS origins for frontend

### 4. Database Setup

```powershell
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py create_sample_data
```

### 5. Run Development Server

```powershell
python manage.py runserver
```

The API will be available at: `http://localhost:8000`

## 📚 API Documentation

Once the server is running, access:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## 🔑 API Endpoints

### Authentication
- `POST /api/auth/register/` - Customer registration
- `POST /api/auth/login/` - Login (JWT tokens)
- `POST /api/auth/refresh/` - Refresh access token
- `POST /api/auth/logout/` - Logout
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update profile
- `POST /api/auth/change-password/` - Change password

### Farmers (Admin/Staff)
- `GET /api/farmers/` - List farmers (with filters)
- `POST /api/farmers/` - Create farmer
- `GET /api/farmers/{id}/` - Farmer detail
- `PUT /api/farmers/{id}/` - Update farmer
- `PATCH /api/farmers/{id}/approve/` - Approve farmer
- `GET /api/farmers/{id}/supply-history/` - Supply history
- `POST /api/farmers/{id}/record-supply/` - Record supply
- `POST /api/farmers/{id}/record-payment/` - Record payment
- `GET /api/farmers/reports/` - Farmer reports

### Customers
- `GET /api/customers/` - List customers (Admin only)
- `GET /api/customers/me/` - Current customer profile
- `PUT /api/customers/me/` - Update own profile

### Products (Public read, Admin write)
- `GET /api/products/` - List products
- `POST /api/products/` - Create product (Admin)
- `GET /api/products/{id}/` - Product detail
- `PUT /api/products/{id}/` - Update product (Admin)

### Pricing (Public read, Admin write)
- `GET /api/pricing/` - List prices
- `GET /api/pricing/current/` - Current prices
- `GET /api/pricing/history/` - Price history
- `POST /api/pricing/` - Add price (Admin)

### Inventory (Admin/Staff)
- `GET /api/inventory/stock/` - List stock
- `POST /api/inventory/stock/` - Add stock
- `GET /api/inventory/stock/{id}/` - Stock detail
- `GET /api/inventory/alerts/` - Low stock & expiry alerts
- `POST /api/inventory/deduct/` - Manual deduction
- `POST /api/inventory/transfer/` - Warehouse transfer
- `GET /api/inventory/movements/` - Movement history

### Orders
- `GET /api/orders/` - List orders
- `POST /api/orders/` - Create order (Customer)
- `GET /api/orders/{id}/` - Order detail
- `PATCH /api/orders/{id}/approve/` - Approve order (Admin)
- `PATCH /api/orders/{id}/cancel/` - Cancel order
- `PATCH /api/orders/{id}/update_status/` - Update status (Admin)
- `GET /api/orders/history/` - Order history

### Blog (Public read, Admin write)
- `GET /api/blog/` - List published posts
- `POST /api/blog/` - Create post (Admin)
- `GET /api/blog/{slug}/` - Post detail
- `PUT /api/blog/{slug}/` - Update post (Admin)

## 👤 Default Login Credentials (After running create_sample_data)

```
Admin:
  Username: admin
  Password: admin123

Staff:
  Username: staff
  Password: staff123

Customer:
  Username: john_doe
  Password: password123
```

## 🔧 Management Commands

### Check Stock Alerts
```powershell
python manage.py check_stock_alerts
```

### Generate Business Reports
```powershell
# Last 30 days (default)
python manage.py generate_reports

# Custom period
python manage.py generate_reports --days 90
```

### Create Sample Data
```powershell
python manage.py create_sample_data
```

## 📊 Admin Dashboard

Access the Django admin at: `http://localhost:8000/admin/`

Features:
- User management
- Customer analytics
- Farmer approvals
- Stock monitoring
- Order processing
- Price updates
- Blog management

## 🏗️ Project Structure

```
maize_point/
├── accounts/           # User authentication & profiles
├── customers/          # Customer management
├── farmers/            # Farmer & supply management
├── products/           # Product catalog
├── pricing/            # Price management
├── inventory/          # Stock & warehouse management
├── orders/             # Order processing
├── blog/               # Content management
├── notifications/      # Email/SMS notifications
├── maize_point/        # Project settings
├── media/              # Uploaded files
├── manage.py
└── requirements.txt
```

## 🔒 Security Features

- JWT authentication with access/refresh tokens
- Password hashing with Django's PBKDF2
- CORS configuration for frontend integration
- Input validation and sanitization
- Role-based permissions (Admin, Staff, Customer)
- Secure file upload handling

## 📦 Key Technologies

- **Django 4.2**: Web framework
- **Django REST Framework**: API toolkit
- **PostgreSQL**: Primary database
- **JWT**: Token-based authentication
- **Celery**: Async task processing
- **Redis**: Message broker & caching
- **Pillow**: Image processing
- **drf-spectacular**: API documentation

## 🚀 Production Deployment

### Environment Variables

Set these in production:
```
DEBUG=False
SECRET_KEY=<strong-secret-key>
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:pass@host:5432/dbname
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

### Security Settings

Uncomment in `.env` for production:
```
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Static Files

```powershell
python manage.py collectstatic
```

## 🧪 Testing

```powershell
python manage.py test
```

## 📝 API Response Format

### Success Response
```json
{
  "id": 1,
  "field1": "value1",
  "field2": "value2"
}
```

### Error Response
```json
{
  "field_name": ["Error message"],
  "non_field_errors": ["General error"]
}
```

### Paginated Response
```json
{
  "count": 100,
  "next": "http://api.example.org/accounts/?page=4",
  "previous": "http://api.example.org/accounts/?page=2",
  "results": [...]
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is proprietary software for Maize Supply & Storage Enterprise.

## 📞 Support

For issues or questions, contact the development team.

## 🔄 Recent Updates

- ✅ Complete API implementation
- ✅ JWT authentication
- ✅ Automated stock management
- ✅ Email notifications
- ✅ Comprehensive reporting
- ✅ API documentation
- ✅ Sample data generation

## 🎯 Future Enhancements

- SMS notifications integration
- Advanced analytics dashboard
- Mobile app API optimization
- Real-time stock updates with WebSockets
- Automated backup system
- Multi-language support
