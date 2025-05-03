from app import db
from app.models.log import Log  # type: ignore


def log_action(action, status_code):
    """
    Logs the action performed and the corresponding status code to the database.
    Example: If a user creates a ticket, you log the action 'Ticket Created' with a 201 status code.
    """
    log = Log(action=action, status_code=status_code)
    db.session.add(log)
    db.session.commit()
