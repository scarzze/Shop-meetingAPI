import click
from flask.cli import with_appcontext
from .models.user import db, User

@click.command('create-support-agent')
@click.argument('email')
@click.argument('password')
@click.argument('first_name')
@click.argument('last_name')
@with_appcontext
def create_support_agent(email, password, first_name, last_name):
    """Create a new support agent user"""
    try:
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='support_agent'
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        click.echo(f"Support agent created successfully: {email}")
    except Exception as e:
        click.echo(f"Error creating support agent: {str(e)}")
        db.session.rollback()