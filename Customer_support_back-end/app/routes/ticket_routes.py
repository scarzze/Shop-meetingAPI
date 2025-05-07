from flask import Blueprint, request, jsonify
from app.models import Ticket
from app import db

ticket_bp = Blueprint('ticket', __name__)

@ticket_bp.route('/ticket', methods=['POST'])
def create_ticket():
    data = request.get_json()
    ticket = Ticket(
        user_id=data['user_id'],
        subject=data['subject'],
        description=data['description']
    )
    db.session.add(ticket)
    db.session.commit()
    return jsonify({"message": "Ticket created successfully"}), 201

@ticket_bp.route('/ticket/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    ticket = db.session.query(Ticket).get(ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404
    return jsonify({
        "id": ticket.id,
        "subject": ticket.subject,
        "description": ticket.description,
        "status": ticket.status,
        "created_at": ticket.created_at
    })

@ticket_bp.errorhandler(404)
def ticket_not_found(error):
    return jsonify({"error": "Ticket not found"}), 404