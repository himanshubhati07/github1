.PHONY: build run stop clean docker-build docker-up docker-down

PORT=55513

build:
	mvn package -DskipTests -q

run: build
	java -jar target/*.jar --server.port=$(PORT)

stop:
	@echo "Send SIGTERM to the Java process to stop it."

clean:
	mvn clean -q

docker-build:
	docker build -t attendance-app .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

logs:
	docker-compose logs -f app

health:
	curl -s http://localhost:$(PORT)/actuator/health | python3 -m json.tool

test-login:
	curl -s -X POST http://localhost:$(PORT)/api/v1/auth/login \
	  -H "Content-Type: application/json" \
	  -d '{"email":"admin@company.com","password":"Admin@123"}' | python3 -m json.tool
