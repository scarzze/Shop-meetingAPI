# Orderservice API

This is a Flask-based Orderservice API that manages customer orders, order items, return requests, and order status history.

## Setup

### Database

This project uses a SQLite database file located at `Orderservice/instance/orderservice.db`.

To create and seed the database with sample data, run the following command:

```bash
python3 Orderservice/seed.py
```

This will create the database file and populate it with sample orders, order items, return requests, and order status history.

### Running the Application

To start the Flask application, run:

```bash
python3 Orderservice/app.py
```

The app will start in debug mode and connect to the SQLite database.

## API Endpoints

- `/orders/user/<user_id>`: Get order history for a specific user.
- `/orders/<order_id>`: Get details for a specific order.
- `/orders/<order_id>/status`: Get or update order status.
- `/orders/<order_id>/cancel`: Request order cancellation.
- `/returns`: Request a return for an order or item.
- `/returns/<return_id>`: Get status of a return request.
- `/returns/<return_id>/process`: Process a return request (admin only).

## Notes

- The database file must be accessible and writable by the application.
- Email settings in `app.py` should be configured with valid SMTP credentials for email notifications.
