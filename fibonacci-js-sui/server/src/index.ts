import { startServer, BaseApplication, StepEvent } from '@sparsity/abci';


// customized app logic
export class Application extends BaseApplication {
    private result: number;

    constructor() {
        super();
        this.result = 0;
    }
    
    init(initial_data: string) {
        if (initial_data != "") { 
            console.log("initial_data", initial_data);
            const input = parseInt(initial_data);
            
            this.result = this.fibonacci(input);
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
        return this.result.toString();
    }
}

startServer(new Application());
