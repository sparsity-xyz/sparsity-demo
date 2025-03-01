
run:
	INIT_DATA=${INIT_DATA} npm run app

build:
	docker build --platform linux/amd64 -t abci-fib:latest .
	docker tag abci-fib:latest sparsityxyz/abci-fib:latest

push:
	docker login
	docker push sparsityxyz/abci-fib:latest
