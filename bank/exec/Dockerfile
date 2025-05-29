FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y iproute2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY exec/requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /app

# replace app with the agent app
COPY exec .

# Accept build-time arguments and set as environment variables
ARG VSOCK=false
ARG DNS=true
ENV VSOCK=${VSOCK}
ENV DNS=${DNS}

CMD ["python3", "/app/app.py"]
