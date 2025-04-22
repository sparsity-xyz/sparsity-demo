
run:
	INIT_DATA=${INIT_DATA} npm run app

build:
	docker build --platform linux/amd64 -t abci-fib-sui:latest .
	docker tag abci-fib-sui:latest sparsityxyz/abci-fib-sui:latest

push:
	docker login
	docker push sparsityxyz/abci-fib-sui:latest

