"""
Script to list all registered routes in the Flask application.
"""
from app import create_app

app = create_app()

print("=== All Registered Routes ===")
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint} -> {rule.rule} [{', '.join(rule.methods)}]")

print("\n=== Health Route Specifically ===")
for rule in app.url_map.iter_rules():
    if 'health' in rule.rule:
        print(f"Rule: {rule.rule}")
        print(f"Endpoint: {rule.endpoint}")
        print(f"Methods: {rule.methods}")
        print(f"Defaults: {rule.defaults}")
        print("---")
