
## bridge
### OS
```
// for macos
mv bridge-arm64 bridge

// for linux
mv bridge-amd64 bridge
```

### run bridge
```
./bridge --local
```

## fleet
### OS
```
// for macos
mv fleet-arm64 bridge

// for linux
mv fleet-amd64 bridge
```

### init fleet
```
cp .env.example .env
./fleet init --home .data --local
```

### register to contract
remember everytime you restart the node, you should register again
```
./fleet register --home .data --ip 127.0.0.1
```

### start fleet
```
./fleet run --home .data
```
