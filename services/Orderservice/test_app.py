import pytest
import json
from unittest.mock import patch
from models import Order, ReturnRequest
import pytest
import json
from unittest.mock import patch
from app import create_app, db
import datetime
from models import Order, ReturnRequest

@pytest.fixture
def client():
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'postgresql://orderservice_user:orderservice_pass@localhost:5432/orderservice_test_db'
    }
    app = create_app(test_config)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Seed some test data
            order1 = Order(id='order1', user_id=1, order_date=datetime.date(2023, 1, 1), total_amount=100.0, status='Processing', shipping_address='123 Test St', payment_method='Credit Card')
            order2 = Order(id='order2', user_id=1, order_date=datetime.date(2023, 1, 2), total_amount=150.0, status='Delivered', shipping_address='123 Test St', payment_method='Credit Card')
            db.session.add_all([order1, order2])
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def test_get_order_history(client):
    response = client.get('/orders/user/1')
    assert response.status_code == 200
    data = response.get_json()
    assert 'orders' in data
    assert len(data['orders']) == 2

def test_get_order_details(client):
    response = client.get('/orders/order1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['order_id'] == 'order1'
    assert data['user_id'] == 1

def test_get_order_status(client):
    response = client.get('/orders/order1/status')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data

def test_put_order_status_valid_transition(client):
    with patch('app.send_email') as mock_send_email:
        mock_send_email.return_value = True
        response = client.put('/orders/order1/status', json={'status': 'Shipped'})
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        mock_send_email.assert_called_once()

def test_put_order_status_invalid_transition(client):
    response = client.put('/orders/order1/status', json={'status': 'Delivered'})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_put_order_status_missing_status(client):
    response = client.put('/orders/order1/status', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_put_order_status_invalid_json(client):
    response = client.put('/orders/order1/status', data='notjson', content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_cancel_order(client):
    response = client.post('/orders/order1/cancel', json={'reason': 'Changed my mind'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data

def test_cancel_order_invalid_status(client):
    # Change order status to Shipped to test invalid cancellation
    with app.app_context():
        order = Order.query.get('order1')
        order.status = 'Shipped'
        db.session.commit()
    response = client.post('/orders/order1/cancel', json={'reason': 'Changed my mind'})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_cancel_order_missing_reason(client):
    response = client.post('/orders/order1/cancel', json={})
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data

def test_request_return(client):
    response = client.post('/returns', json={'order_id': 'order2', 'user_id': 1, 'reason': 'Damaged item'})
    assert response.status_code == 201
    data = response.get_json()
    assert 'return_id' in data

def test_request_return_duplicate(client):
    client.post('/returns', json={'order_id': 'order2', 'user_id': 1, 'reason': 'Damaged item'})
    response = client.post('/returns', json={'order_id': 'order2', 'user_id': 1, 'reason': 'Damaged item'})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_request_return_invalid_status(client):
    # Change order status to Processing to test invalid return
    with app.app_context():
        order = Order.query.get('order2')
        order.status = 'Processing'
        db.session.commit()
    response = client.post('/returns', json={'order_id': 'order2', 'user_id': 1, 'reason': 'Damaged item'})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_request_return_missing_fields(client):
    response = client.post('/returns', json={'order_id': 'order2'})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_get_return_status(client):
    client.post('/returns', json={'order_id': 'order2', 'user_id': 1, 'reason': 'Damaged item'})
    return_request = ReturnRequest.query.first()
    response = client.get(f'/returns/{return_request.id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['return_id'] == return_request.id

def test_process_return_approve(client):
    client.post('/returns', json={'order_id': 'order2', 'user_id': 1, 'reason': 'Damaged item'})
    return_request = ReturnRequest.query.first()
    with patch('app.send_email') as mock_send_email:
        mock_send_email.return_value = True
        response = client.put(f'/returns/{return_request.id}/process', json={'action': 'approve', 'resolution': 'Approved'})
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        mock_send_email.assert_called_once()

def test_process_return_reject(client):
    client.post('/returns', json={'order_id': 'order2', 'user_id': 1, 'reason': 'Damaged item'})
    return_request = ReturnRequest.query.first()
    with patch('app.send_email') as mock_send_email:
        mock_send_email.return_value = True
        response = client.put(f'/returns/{return_request.id}/process', json={'action': 'reject', 'resolution': 'Rejected'})
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        mock_send_email.assert_called_once()

def test_process_return_invalid_action(client):
    client.post('/returns', json={'order_id': 'order2', 'user_id': 1, 'reason': 'Damaged item'})
    return_request = ReturnRequest.query.first()
    response = client.put(f'/returns/{return_request.id}/process', json={'action': 'invalid'})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
