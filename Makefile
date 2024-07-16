ifneq (,$(wildcard ./.env))
    include .env
    export
endif

# Define image name and tag
IMAGE_NAME := onnecta-llm-service
TAG := latest

build:
	docker build -t $(IMAGE_NAME):$(TAG) -f Dockerfile .

run:
	docker run -dp 8000:8000 --name $(IMAGE_NAME) --env-file .env $(IMAGE_NAME):$(TAG)

