# ag2-abci-server
## requirements

```
pip install -r requirements.txt
```

## create an API-KEY for agent
```
cp api_key_example.json api_key.json
```
## edit the api_key.json
```
[
  {
    "model": "gpt-4o-mini",
    "api_key": "<API_KEY_HERE>"
  }
]
```

## test run
```
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 src/ag2_abci_app.py
```
