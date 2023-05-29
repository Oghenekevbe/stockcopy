// function createTransaction() {
//     // Fetch the data from the API
//     fetch('/stock_transactions_api/')
//       .then(response => response.json())
//       .then(data => {
//         // Check if data is an array
//         if (Array.isArray(data)) {
//           // Choose a random stock and portfolio from the results
//           const stocks = data.map(transaction => transaction.fields.stock);
//           const randomStock = stocks[Math.floor(Math.random() * stocks.length)];
  
//           const portfolios = data.map(transaction => transaction.fields.portfolio);
//           const randomPortfolio = portfolios[Math.floor(Math.random() * portfolios.length)];
  
//           // Choose a random transaction type
//           const transactionTypes = ['BUY', 'SELL'];
//           const randomTransactionType = transactionTypes[Math.floor(Math.random() * transactionTypes.length)];
  
//           // Choose random values for quantity and price
//           const randomQuantity = Math.floor(Math.random() * 10) + 1;
//           const randomPrice = Math.floor(Math.random() * 50) + 20;
  
//           // Create the new transaction object and send it to the API
//           const newTransaction = {
//             stock: randomStock,
//             portfolio: randomPortfolio,
//             quantity: randomQuantity,
//             price: randomPrice,
//             transaction_type: randomTransactionType
//           };
  
//           fetch('/stock_transactions_api/', {
//             method: 'POST',
//             headers: {
//               'Content-Type': 'application/json'
//             },
//             body: JSON.stringify(newTransaction)
//           })
//             .then(response => response.json())
//             .then(data => console.log(data))
//             .catch(error => console.error(error));
//         } else {
//           // Loop through the data
//           for (let i = 0; i < data.length; i++) {
//             const transaction = data[i];
            
//             // Check if transaction is defined
//             if (transaction) {
//               // Choose a random stock and portfolio from the transaction
//               const stock = transaction.fields ? transaction.fields.stock : null;
//               const portfolio = transaction.fields ? transaction.fields.portfolio : null;
//               if (stock && portfolio) {
//                 // Choose a random transaction type
//                 const transactionTypes = ['BUY', 'SELL'];
//                 const randomTransactionType = transactionTypes[Math.floor(Math.random() * transactionTypes.length)];
  
//                 // Choose random values for quantity and price
//                 const randomQuantity = Math.floor(Math.random() * 10) + 1;
//                 const randomPrice = Math.floor(Math.random() * 50) + 20;
  
//                 // Create the new transaction object and send it to the API
//                 const newTransaction = {
//                   stock: stock,
//                   portfolio: portfolio,
//                   quantity: randomQuantity,
//                   price: randomPrice,
//                   transaction_type: randomTransactionType
//                 };
  
//                 fetch('/stock_transactions_api/', {
//                   method: 'POST',
//                   headers: {
//                     'Content-Type': 'application/json'
//                   },
//                   body: JSON.stringify(newTransaction)
//                 })
//                   .then(response => response.json())
//                   .then(data => console.log(data))
//                   .catch(error => console.error(error));
//               }
//             }
//           }
//         }
//       })
//       .catch(error => console.error(error));
//   }
  
//   // Call the createTransaction function every minute
//   setInterval(createTransaction, 60000);

function createRandomTransaction() {
    // Generate a random transaction type ('BUY' or 'SELL')
    const transactionType = Math.random() < 0.5 ? 'BUY' : 'SELL';

    // Retrieve the CSRF token from the cookie
    const csrfToken = getCookie('csrftoken');

    // Make a POST request to create a new transaction
    fetch('stock_transactions_api', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,  // Include the CSRF token in the request headers
        },
        body: JSON.stringify({
            transaction_type: transactionType,
        }),
    })
    .then(response => response.json())
    .then(data => {
        // Transaction created successfully
        console.log('New transaction created:', data);
    })
    .catch(error => {
        // Error occurred while creating the transaction
        console.error('Error creating transaction:', error);
    });
}

// Call the createRandomTransaction function initially
createRandomTransaction();

// Schedule the function to be executed every 1 minute
setInterval(createRandomTransaction, 60000);

// Function to retrieve the value of a cookie by name
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return parts.pop().split(';').shift();
    }
}
