let globalVariable = 0;

async function asyncFunction() {
    // Simulate some asynchronous operation, like fetching data from an API
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Change the global variable
    globalVariable = 10;
    
    console.log("Inside asyncFunction:", globalVariable);
}

console.log("Before asyncFunction:", globalVariable);

asyncFunction();

console.log("After asyncFunction:", globalVariable);