FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set PYTHONPATH
ENV PYTHONPATH=":/app/cometbft:/app/gogoproto:/app/proto"

CMD ["python", "src/ag2_abci_app.py"]
