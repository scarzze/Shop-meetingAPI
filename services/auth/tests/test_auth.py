import sys
import os
import pytest
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from services.auth.src.app import app
from shared.database import db
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
        db.session.remove()
        db.drop_all()

def test_register(client):
    # Test successful registration
    response = client.post('/auth/register',
        json={'email': 'test@example.com', 'password': 'password123'})
    assert response.status_code == 201
    assert 'email' in response.json
    assert response.json['email'] == 'test@example.com'

    # Test duplicate email
    response = client.post('/auth/register',
        json={'email': 'test@example.com', 'password': 'password123'})
    assert response.status_code == 409

    # Test invalid email
    response = client.post('/auth/register',
        json={'email': 'invalid-email', 'password': 'password123'})
    assert response.status_code == 400

def test_login(client):
    # Register a user first
    client.post('/auth/register',
        json={'email': 'test@example.com', 'password': 'password123'})

    # Test successful login
    response = client.post('/auth/login',
        json={'email': 'test@example.com', 'password': 'password123'})
    assert response.status_code == 200
    assert 'access_token' in response.json
    assert 'user' in response.json

    # Test invalid credentials
    response = client.post('/auth/login',
        json={'email': 'test@example.com', 'password': 'wrongpassword'})
    assert response.status_code == 401

def test_verify_token(client):
    # Register and login to get token
    client.post('/auth/register',
        json={'email': 'test@example.com', 'password': 'password123'})
    response = client.post('/auth/login',
        json={'email': 'test@example.com', 'password': 'password123'})
    token = response.json['access_token']

    # Test verify token endpoint
    response = client.get('/auth/verify',
        headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert 'email' in response.json

    # Test verify without token
    response = client.get('/auth/verify')
    assert response.status_code == 401

def test_rate_limiting(client):
    # Test rate limiting on register
    for i in range(6):
        response = client.post('/auth/register',
            json={'email': f'test{i}@example.com', 'password': 'password123'})
        if i >= 5:
            assert response.status_code == 429  # Too many requests

    # Test rate limiting on login
    for i in range(6):
        response = client.post('/auth/login',
            json={'email': 'test@example.com', 'password': 'password123'})
        if i >= 5:
            assert response.status_code == 429  # Too many requests