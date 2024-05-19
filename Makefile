ifneq (,$(wildcard ./.env))
    include .env
    export
endif

# Define image name and tag
IMAGE_NAME := project-onnecta
TAG := latest

build:
	docker build -t $(IMAGE_NAME):$(TAG) -f Dockerfile .

run:
	docker run -dp 8000:8000 --name $(IMAGE_NAME) $(IMAGE_NAME):$(TAG)

