x.PHONY: init start stop graceful-stop status migrate validate diagnose clean health

# Initialize everything
init:
	@echo "Initializing services..."
	chmod +x *.py *.sh
	./init_databases.sh
	./manage_migrations.py init
	./manage_migrations.py migrate
	./validate_configs.py
	./validate_service_registry.py

# Start all services
start:
	@echo "Starting services..."
	docker-compose up -d
	@echo "Waiting for services to start..."
	sleep 10
	./diagnose_services.py

# Stop all services immediately
stop:
	@echo "Stopping services..."
	docker-compose down

# Stop services gracefully
graceful-stop:
	@echo "Gracefully stopping services..."
	./graceful_shutdown.py

# Check service status
status:
	@echo "Checking service status..."
	./health_checker.py

# Run database migrations
migrate:
	@echo "Running database migrations..."
	./manage_migrations.py migrate

# Validate configurations
validate:
	@echo "Validating configurations..."
	./validate_configs.py
	./validate_service_registry.py

# Run diagnostics
diagnose:
	@echo "Running diagnostics..."
	./diagnose_services.py

# Monitor service health
health:
	@echo "Monitoring service health..."
	./health_checker.py

# Clean up
clean:
	@echo "Cleaning up..."
	docker-compose down -v
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.log" -delete
	find . -type f -name "*.json" -delete