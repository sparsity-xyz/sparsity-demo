build:
	docker build --platform linux/amd64 -t abci-ag2-py:latest .
	docker tag abci-ag2-py:latest sparsityxyz/abci-ag2-py:latest

push:
	docker login
	docker push sparsityxyz/abci-ag2-py:latest
