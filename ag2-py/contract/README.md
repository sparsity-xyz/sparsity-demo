## App Contract  

### Local Chain Network Setup  
Use the following command to start the local chain node:  
```sh
make node
```

## Manually Create a Session
```sh
make startChat
```

### Manually Check a Session  
```sh
make session SID=0
```

### Callback Session  
```sh
make callback-session SID=0
```

### Settle the Result  
Once the result is from the server, settle it using this command:  
```sh
make callback-settle SID=0 RESULT=0x000000000000000000000000f39fd6e51aad88f6f4ce6ab8827279cfffb9226600000000000000000000000070997970c51812dc3a010c7d01b50e0d17dc79c8000000000000000000000000f39fd6e51aad88f6f4ce6ab8827279cfffb92266
``` 