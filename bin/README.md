
## bridge
### pull image
```
docker pull sparsityxyz/bridge
```

### run bridge
```
# macos
docker run --rm -ti -e HOST=host.docker.internal sparsityxyz/bridge

# linux
docker run --rm -ti -e HOST=172.17.0.1 sparsityxyz/bridge
```

## fleet
### pull image
```
docker pull sparsityxyz/fleet
```

### init fleet
```
docker run -ti --rm -v ./.data:/root/.fleet -v /var/run/docker.sock:/var/run/docker.sock sparsityxyz/fleet fleet init --local
```

### register to contract
remember everytime you restart the node, you should register again
```
# macos
docker run -ti --rm -v ./.data:/root/.fleet -v /var/run/docker.sock:/var/run/docker.sock sparsityxyz/fleet fleet register --ip 127.0.0.1

# linux
TODO
```

### start fleet
```
# macos
docker run -ti --rm -v ./.data:/root/.fleet -v /var/run/docker.sock:/var/run/docker.sock sparsityxyz/fleet fleet run

# linux
TODO
```
