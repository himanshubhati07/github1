#!/bin/bash
SERVER_PORT=55513

echo "Building application..."
mvn package -DskipTests -q

echo "Starting application on port $SERVER_PORT..."
java -jar target/*.jar --server.port=$SERVER_PORT
