from datetime import datetime, timedelta
from models import db, Order, OrderItem, ReturnRequest, ReturnItem, OrderStatusHistory
from app import create_app  # Import create_app function

app = create_app()  # Create app instance

def seed_data():
    with app.app_context():
        # Create all tables
        db.create_all()

        # Clear existing data
        ReturnItem.query.delete()
        ReturnRequest.query.delete()
        OrderItem.query.delete()
        OrderStatusHistory.query.delete()
        Order.query.delete()
        db.session.commit()

        # Create sample orders
        order1 = Order(
            user_id=1,
            order_date=datetime.utcnow() - timedelta(days=10),
            total_amount=150.00,
            status='Delivered',
            shipping_address='123 Main St, Springfield',
            billing_address='123 Main St, Springfield',
            payment_method='Credit Card',
            payment_status='Completed',
            tracking_number='TRACK123456',
            estimated_delivery=datetime.utcnow() - timedelta(days=2)
        )

        order2 = Order(
            user_id=2,
            order_date=datetime.utcnow() - timedelta(days=5),
            total_amount=75.50,
            status='Processing',
            shipping_address='456 Elm St, Shelbyville',
            billing_address='456 Elm St, Shelbyville',
            payment_method='PayPal',
            payment_status='Pending',
            tracking_number=None,
            estimated_delivery=None
        )

        # Create order items for order1
        item1 = OrderItem(
            product_id=101,
            product_name='Wireless Mouse',
            quantity=1,
            price=25.00,
            discount=0.0,
            tax_rate=0.07,
            return_status='None'
        )
        item2 = OrderItem(
            product_id=102,
            product_name='Mechanical Keyboard',
            quantity=1,
            price=125.00,
            discount=10.0,
            tax_rate=0.07,
            return_status='None'
        )
        order1.items.extend([item1, item2])

        # Create order items for order2
        item3 = OrderItem(
            product_id=103,
            product_name='USB-C Cable',
            quantity=3,
            price=15.00,
            discount=0.0,
            tax_rate=0.07,
            return_status='None'
        )
        order2.items.append(item3)

        # Add orders to session
        db.session.add(order1)
        db.session.add(order2)
        db.session.commit()

        # Create return request for order1
        return_request1 = ReturnRequest(
            order_id=order1.id,
            user_id=1,
            request_date=datetime.utcnow() - timedelta(days=1),
            reason='Defective keyboard',
            status='Pending',
            resolution=None,
            refund_amount=None,
            refund_method=None
        )

        # Create return item for the return request
        return_item1 = ReturnItem(
            order_item_id=item2.id,
            quantity=1,
            reason='Keys not working',
            condition='Damaged',
            action='Refund',
            amount_refunded=None
        )
        return_request1.items.append(return_item1)

        db.session.add(return_request1)
        db.session.commit()

        # Create order status history entries
        history1 = OrderStatusHistory(
            order_id=order1.id,
            status='Processing',
            changed_at=order1.order_date,
            changed_by='system',
            notes='Order placed'
        )
        history2 = OrderStatusHistory(
            order_id=order1.id,
            status='Shipped',
            changed_at=order1.order_date + timedelta(days=2),
            changed_by='system',
            notes='Order shipped'
        )
        history3 = OrderStatusHistory(
            order_id=order1.id,
            status='Delivered',
            changed_at=order1.order_date + timedelta(days=5),
            changed_by='system',
            notes='Order delivered'
        )
        db.session.add_all([history1, history2, history3])
        db.session.commit()

        print("Database seeded successfully.")

if __name__ == '__main__':
    seed_data()
