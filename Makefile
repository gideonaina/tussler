COMPOSE_FILE := docker-compose.yml
LOCAL_LLM ?= llama3
PROFILE ?= dev

.PHONY: help start stop clean

# ANSI color codes
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m # No Color

help:
	@echo "Usage:"
	@echo "  make start    - Start Docker Compose"
	@echo "  make stop     - Stop Docker Compose"
	@echo "  make clean    - Stop Docker Compose and remove volumes"

start:
	@echo "Running with LOCAL_LLM=$(LOCAL_LLM)"
	LOCAL_LLM=$(LOCAL_LLM) docker-compose --profile $(PROFILE) -f $(COMPOSE_FILE) up

fresh-start:
	@echo "Running with LOCAL_LLM=$(LOCAL_LLM)"
	docker-compose -f $(COMPOSE_FILE) build --no-cache && LOCAL_LLM=$(LOCAL_LLM) docker-compose --profile $(PROFILE) -f $(COMPOSE_FILE) up 

model:
	LOCAL_LLM=$(LOCAL_LLM) docker-compose --profile model -f $(COMPOSE_FILE) up 

stop:
	LOCAL_LLM=$(LOCAL_LLM) docker-compose --profile $(PROFILE) -f $(COMPOSE_FILE) down

clean:
	docker-compose -f $(COMPOSE_FILE) down -v

deep-clean:
	docker-compose -f $(COMPOSE_FILE) down -v --remove-orphans
	docker volume prune -f
	docker network prune -f
	docker stop $(shell docker ps -aq) || $(shell exit 0)
	docker rm $(shell docker ps -aq)
	docker volume rm $(shell docker volume ls -q)
	docker network rm $(shell docker network ls -q)

tussler-dev:
	uvicorn tussler.launcher:app --host 0.0.0.0 --port 8081 --reload

test-ollama:
	@echo "------- Checking Ollama API -----"
	@curl http://localhost:11434/api/tags

test:
	@echo "------- Checking Port 11434 -----"
	@timeout 2s curl -sf http://localhost:11434 > /dev/null && echo "$(GREEN)http://localhost:11434 ok$(NC)" || echo "$(RED)http://localhost:11434 error$(NC)"
	@timeout 2s curl -sf http://127.0.0.1:11434 > /dev/null && echo "$(GREEN)http://127.0.0.1:11434 ok$(NC)"|| echo "$(RED)http://127.0.0.1:11434 error$(NC)"
	@timeout 2s curl -sf http://host.docker.internal:11434 > /dev/null && echo "$(GREEN)host.docker.internal:11434 ok$(NC)"|| echo "$(RED)host.docker.internal:11434 error$(NC)"
	@timeout 2s curl -sf http://0.0.0.0:11434 > /dev/null && echo "$(GREEN)0.0.0.0:11434 ok$(NC)"|| echo "$(RED)0.0.0.0:11434 error$(NC)"
	@timeout 2s curl -sf http://ollama:11434 > /dev/null && echo "$(GREEN)ollama:11434 ok$(NC)"|| echo "$(RED)ollama:11434 error$(NC)"
	
	@echo "---- Checking Port 8080 -----"
	@timeout 2s curl -sf http://localhost:8080 > /dev/null && echo "$(GREEN)http://localhost:8080 ok$(NC)"|| echo "$(RED)http://localhost:8080 error$(NC)"
	@timeout 2s curl -sf http://127.0.0.1:8080 > /dev/null && echo "$(GREEN)http://127.0.0.1:8080 ok$(NC)"|| echo "$(RED)http://127.0.0.1:8080 error$(NC)"
	@timeout 2s curl -sf http://host.docker.internal:8080 > /dev/null && echo "$(GREEN)host.docker.internal:8080 ok$(NC)"|| echo "$(RED)host.docker.internal:8080 error$(NC)"
	@timeout 2s curl -sf http://0.0.0.0:8080 > /dev/null && echo "$(GREEN)0.0.0.0:8080 ok$(NC)"|| echo "$(RED)0.0.0.0:8080 error$(NC)"
	@timeout 2s curl -sf http://open-webui:8080 > /dev/null && echo "$(GREEN)open-webui:8080 ok$(NC)"|| echo "$(RED)open-webui:8080 error$(NC)"
	
	@echo "---- Checking Port 3000 -----"
	@timeout 2s curl -sf http://localhost:3000 > /dev/null && echo "$(GREEN)http://localhost:3000 ok$(NC)"|| echo "$(RED)http://localhost:3000 error$(NC)"
	@timeout 2s curl -sf http://127.0.0.1:3000 > /dev/null && echo "$(GREEN)http://127.0.0.1:3000 ok$(NC)"|| echo "$(RED)http://127.0.0.1:3000 error$(NC)"
	@timeout 2s curl -sf http://host.docker.internal:3000 > /dev/null && echo "$(GREEN)host.docker.internal:3000 ok$(NC)"|| echo "$(RED)host.docker.internal:3000 error$(NC)"
	@timeout 2s curl -sf http://0.0.0.0:3000 > /dev/null && echo "$(GREEN)0.0.0.0:3000 ok$(NC)"|| echo "$(RED)0.0.0.0:3000 error$(NC)"
	@timeout 2s curl -sf http://open-webui:3000 > /dev/null && echo "$(GREEN)open-webui:3000 ok$(NC)"|| echo "$(RED)open-webui:3000 error$(NC)"
