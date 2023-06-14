# AlfaBet Exercise

- [AlfaBet Exercise](#alfabet-exercise)
  * [First task: Perform transactions](#first-task--perform-transactions)
  * [Second task: Generate transactions report](#second-task--generate-transactions-report)
  * [Third task: Performing an advance payment](#third-task--performing-an-advance-payment)
- [Components](#components)
- [Accounts-manager service](#accounts-manager-service)
  * [Choosing a database](#choosing-a-database)
  * [Designing the API](#designing-the-api)
    + [Perform transaction](#perform-transaction)
    + [Generate transactions report](#generate-transactions-report)
    + [Perform a bank transaction](#perform-a-bank-transaction)
- [Advances service](#advances-service)
  * [Concerns](#concerns)

## First task: Perform transactions
Basically given two bank accounts & an amount (& the direction of the transaction), move the money between the accounts.
Special considerations & edge cases:
* Accounts cannot have negative amount of money. If one of the account does not have enough funds, the transaction will fail
* We must make sure that the transaction will not fail in the middle resulting in the money moving out of one account but not entering the other account

## Second task: Generate transactions report
We need to be able to generate a report of the most recent transactions, up to 5 days in the past.
Every transaction in the report will have:
* Transaction ID
* Transaction status (Success/fail)  

Special considerations & edge cases:
* There might be a lot of transactions, we might need to paginate the report result
* While generating the report new transactions might take place, we don't want new transactions in the report while we are paginating through the results.

## Third task: Performing an advance payment
A client can ask for an advance of funds from the bank, which they will return a part of every week until the 12 weeks have passed & the entire amount has been returned.

Special considerations & edge cases:
* If a weekly payment has failed, it will be added to the next payment 
  (or a new payment will be created if this one is the last)
* For a given payment P, only one process/worker/instance can handel it at one time, in order to not withdraw the funds from the account multiple times.

An idea to make sure that we are not missing any payment is to run a task at a constant interval that will find 
advances that do not have enough payments according to this formula:
```
payments = get all payments of the advance that are paid, not due yet or being processed
sum = sum of all payments amounts
if sum != advance amount:
    we are missing advances, alert admins
```

# Components
Thinking about the feature we have here two different responsibilities, and thus should be in two different components:
1. Accounts-manager: Managing bank account funds & transactions between them.
2. Advances-service: Performing advances for clients & keeping track of them.

# Accounts-manager service
Keeps a record of every account & their funds, & performs transactions to move money between these accounts.
Because every action managed by this service is immediate & not scheduled, it will be a simple API service with a database.

## Choosing a database
For storing the accounts & their funds we could use many databases such as:
* MongoDB
* PostgreSQL
* MySQL
* Microsoft SQL Server
* Cassandra

I decided to use an SQL database (PostgreSQL) because of SQLs strong enforcement, easy atomic actions with transactions 
& the support of sql alchemy. If other considerations like cross site replication, higher loads arise a different 
database can be used.

Now when choosing where to store the transactions we have other concerns, such as:
* The number of transactions can be many times larger than the number of accounts
* We usually need access only to the X days amount of transactions, so the other transactions can be kept in "Cold Storage" in order to speed up the creation & management of recent transactions.

Here there are two good choices:
* Use the same postgresql database for transactions, but index the table based on the timestamp for efficiency 
in high scale (you can also divide the data into blocks by date for more efficiency)
* Use a database such as elasticsearch, which excels in large amount of time data

For this exercise I chose to use the postgres db.

## Designing the API
### Perform transaction
```
Method: POST
Route: /api/v1/transaction
Body: {
    "src_account_id": "ID",
    "dst_account_id": "ID",
    "amount": 12.3, // Positive Float
    "direction": "debit" // Possible values: debit (Take from src & give to dst), credit (Take from dst & give to src)
}
Response: {
    "transaction_id": "ID",
    "transaction_timestamp": "2023-07-11 12:01:27.053", // Timestamp
    "src_account_id": "ID",
    "dst_account_id": "ID",
    "amount": 12.3,
    "direction": "debit",
    "status": "fail" // Possible values: success, fail
    "reason": "Insufficient funds" // A reason why the transaction failed. only present when the status is "fail"
}
```
### Generate transactions report
```
Method: GET
Route: /api/v1/transactions
Query params:
    page: 1    // Page of results, used for pagination
    limit: 100 // How many results to show in each page
    start_timestamp: "2023-07-11 12:01:27.053" // Timestamp of the erliest report to collect
    end_timestamp: "2023-07-11 14:01:27.053"   // Timestamp of the latest report to collect
    
Response: {
    "transactions": [
        {
            "transaction_id": "ID",
            "transaction_timestamp": "2023-07-11 12:01:27.053",
            "src_account_id": "ID",
            "dst_account_id": "ID",
            "amount": 12.3,
            "direction": "debit",
            "status": "fail" // Possible values: success, fail
            "reason": "Insufficient funds" // A reason why the transaction failed. only present when the status is "fail"
        },
        {...}
    ],
    "page": 1,
    "limit": 100,
    "total_amount": 135,
    "total_pages": 2
}
```

### Perform a bank transaction
A bank transaction is a transaction without a source account. 
This transaction is used for giving & taking money from accounts as a part of advances.
```
Method: POST
Route: /api/v1/bank_transactions
Body: {
    "dst_account_id": "ID",
    "amount": 12.3, // Positive Float
    "direction": "debit", // Possible values: debit (Take from src), credit (Give to src)
    "reason": "Advance payment week 3" // Why the transaction happened, can be used for tracking
}
Response: {
    "transaction_id": "ID",
    "transaction_timestamp": "2023-07-11 12:01:27.053", // Timestamp
    "dst_account_id": "ID",
    "amount": 12.3,
    "direction": "debit",
    "status": "fail" // Possible values: success, fail
    "reason": "Insufficient funds" // A reason why the transaction failed. only present when the status is "fail"
}
```

# Advances service
Keeps record of every advancement & the related payments, and uses the accounts manager API to grant / withdraw the amounts from the account.

This service has multiple parts:
* Database - stores all advances & payments
* API - exposing the "perform advance" functionality
* Celery broker - a broker acting as a message que for managing tasks
* Celery worker - A worker node that runs tasks that withdraw payments from accounts
* Celery beat - periodically triggers tasks for processing payments

## Concerns
* because the accounts are managed on another service, 
  there a risk of an unexpected failure after updating the account funds, 
  but before updating the payment status.
  In order to minimise that risk, straight after updating the account funds we will update the payment in our db. 
  If even this section fails we will raise a critical error which will be caught by our log monitoring system.
* We need to be sure that only one worker & one process handles any single payment, so
  here we relay on the celery task management where every worker pulls a task from the queue & other workers cannot 
  pull the same task unless the original task fails.
