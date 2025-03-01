# Local Testing  

`INIT_DATA` represents the ABI-encoded data from the contract.  

For example, if we want to compute `fib(22)`, the corresponding `INIT_DATA` should be:  

```sh
0x0000000000000000000000000000000000000000000000000000000000000016
```

You can retrieve the **testing `INIT_DATA`** from contract testing and run the following command:  

```sh
INIT_DATA=0x0000000000000000000000000000000000000000000000000000000000000016 make run
```

The **encoded result** obtained from this process is the data that will be settled back into the contract.  
