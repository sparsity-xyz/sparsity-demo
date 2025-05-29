build-local:
	docker build -f exec/Dockerfile -t bank-local . --build-arg VSOCK=false --build-arg DNS=true

build-enclave:
	docker build -f exec/Dockerfile -t bank-enclave --build-arg VSOCK=true --build-arg DNS=false .

run-local:
	docker run -p 9982:9982 bank-local

run-enclave:
	docker run -p 9982:9982 bank-enclave

run-host:
	python host/main.py