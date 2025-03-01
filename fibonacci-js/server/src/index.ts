import { ethers } from "ethers";
import { startServer, BaseApplication, StepEvent } from '@sparsity/abci';


// customized app logic
export class Application extends BaseApplication {
    private result: number;

    constructor() {
        super();
        this.result = 0;
    }
    
    init(initial_data: string) {
        // the initial_data is the data from contract
        if (initial_data != "") {
            const decoded = ethers.AbiCoder.defaultAbiCoder().decode(['uint256'], initial_data);
            this.result = this.fibonacci(Number(decoded[0]));
            console.log("fib result", this.result);
            console.log("fib encode result", this.resultData())
        } else {
            // it can be empty string if no initial data sent by contract
            this.result = 1;
            console.log("no inital data")
        }
    }

    step(messages: Array<any>): Array<StepEvent> {
        var events: Array<StepEvent> = [];
        return events;
    }

    status(): [isEnd: boolean, data: string] {
        // set isEnd to true if CORE finished calculating the number
        if (this.result == 0) {
            return [false, ""];
        }
        // the data should be encoded with abi
        return [true, this.resultData()];
    }

    fibonacci(n: number): number {
        if (n <= 0) return 0;
        if (n === 1) return 1;
        return this.fibonacci(n - 1) + this.fibonacci(n - 2);
    }

    resultData() {
        return ethers.AbiCoder.defaultAbiCoder().encode(["uint256"], [this.result]);
    }
}

startServer(new Application());
