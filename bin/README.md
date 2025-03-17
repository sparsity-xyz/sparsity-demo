
## bridge
### pull image
```
docker pull sparsityxyz/bridge:latest
```

### run bridge
```
# macos
docker run --rm -ti -e HOST=host.docker.internal sparsityxyz/bridge:latest

# linux
docker run --rm -ti -e HOST=172.17.0.1 sparsityxyz/bridge:latest
```

## fleet
### pull image
```
docker pull sparsityxyz/fleet:latest
```

### init fleet
```
# macos
docker run -ti --rm \
    -v ./.data:/root/.fleet \
    -v /var/run/docker.sock:/var/run/docker.sock \
    sparsityxyz/fleet:latest \
    fleet init --local

# linux
docker run -ti --rm \
    -v ./.data:/root/.fleet \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --add-host=host.docker.internal:172.17.0.1 \
    sparsityxyz/fleet:latest \
    fleet init --local
```

### register to contract
remember everytime you restart the node, you should register again
```
# macos
docker run -ti --rm \
    -v ./.data:/root/.fleet \
    -v /var/run/docker.sock:/var/run/docker.sock \
    sparsityxyz/fleet:latest \
    fleet register --ip 127.0.0.1

# linux
docker run -ti --rm \
    -v ./.data:/root/.fleet \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --add-host=host.docker.internal:172.17.0.1 \
    sparsityxyz/fleet:latest \
    fleet register --ip 127.0.0.1
```

### start fleet
```
# macos
docker run -ti --rm \
    -v ./.data:/root/.fleet \
    -v /var/run/docker.sock:/var/run/docker.sock \
     sparsityxyz/fleet:latest \
    fleet fleet run

# linux
docker run -ti --rm \
    -v ./.data:/root/.fleet \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --add-host=host.docker.internal:172.17.0.1 \
    sparsityxyz/fleet:latest \
    fleet fleet run
```
