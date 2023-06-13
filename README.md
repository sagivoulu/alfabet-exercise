# alphabet-exercise

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
* If a weekly payment has failed, it will be paid on the 13th week (one week after the last payment).
* If there are multiple failed payments, the payment on the 13th week will include the sum of the amounts owed.
* If the last payment on the 13th week also fails, it will be moved to the 14th week & so on...

# Components:
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
I will be using MongoDB because of its dynamic nature, but if other considerations like cross site replication, higher loads arise a different database can be used.

Now when choosing where to store the transactions we have other concerns, such as:
* The number of transactions can be many times larger than the number of accounts
* We usually need access only to the X days amount of transactions, so the other transactions can be kept in "Cold Storage" in order to speed up the creation & management of recent transactions.
In order to store the transactions I would recommend storing them in Elasticsearch, & creating a different index for every day.
That way, when generating the report we can query only the X days of data indices, but still storing every transaction.

## Designing the API
### Perform transaction
```
Method: POST
Route: /api/v1/transaction
Body: {
    "src_account_id": "GUID",
    "dst_account_id": "GUID",
    "amount": 12.3, // Positive Float
    "direction": "debit" // Possible values: debit (Take from src & give to dst), credit (Take from dst & give to src)
}
Response: {
    "transaction_id": "GUID",
    "src_account_id": "GUID",
    "dst_account_id": "GUID",
    "amount": 12.3,
    "direction": "debit",
    "status": "fail" // Possible values: success, fail
    "reason": "Insufficient funds" // A reason why the transaction failed. only present when the status is "fail"
}
```