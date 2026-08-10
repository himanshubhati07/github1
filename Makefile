.PHONY: install run seed test lint docker-build docker-up docker-down

install:
	pip install -r requirements.txt

run:
	PYTHONUNBUFFERED=1 uvicorn app.main:app --host 0.0.0.0 --port 53677 --reload

seed:
	python3 seed.py

test:
	pytest tests/ -v --tb=short

docker-build:
	docker build -t face-attendance-api .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
