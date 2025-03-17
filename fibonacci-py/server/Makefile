IMAGE_NAME := py-abci-fib
IMAGE_TAG := latest

docker-build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

docker-stop:
	docker stop $(CONTAINER_NAME)

docker-clean:
	docker rm $(CONTAINER_NAME)
	docker rmi $(IMAGE_NAME):$(IMAGE_TAG)

docker-up: docker-build docker-run

docker-down: docker-stop docker-clean
