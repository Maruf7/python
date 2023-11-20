# Maruf Assignment

# The Solution is that, one customer can have multiple different accounts.
# Hence the customer Id will be same for multiple accounts and not dynamically generated unlike for Account.
# Since one account cannot be owned by multiple customers here.

from datetime import datetime # Import datatime to get current timestap
import hashlib # Import hashlib for md5 encryption
from threading import * # Import threading for Semaphore

# Class Account 
class Account: 
    semaphore_acc_number = Semaphore(1) # Creating a Semaphore with value 1, so that each account will have a unique account number
    acc_number  = 1  # Initaial account number as 1
    
    def __init__(self, customer_id, balance = 0):
        self.account = Account
        self.account.semaphore_acc_number.acquire() # Start of Semaphore
        self.account_id  = hashlib.md5((str(customer_id)+str(self.account.acc_number)).encode()).hexdigest() # Generate a unique hex code for account Id.
        self.customer_id = customer_id
        self.account_number = self.account.acc_number
        self.balance = balance
        self.account.acc_number += 1
        self.account.semaphore_acc_number.release() # End of Semaphore

    def deposit(self, amount):
        self.balance = self.balance + amount
        return self.balance
    
    def withdraw(self, amount):
        try: 
            check = self.balance - amount
            if check < 0:
                raise ValueError
            else:
                self.balance = self.balance - amount
                return self.balance
        except ValueError :
            print("Not Enough Balance to withdraw.")
            return -1

    def get_balance(self):
        return self.balance



# Class Account Repository
class AccountRepository:
    acc = {} # This will details of all accounts and transactions along with timestamp. 
    def __init__(self):
        self.account_repository = AccountRepository
        
    def save_account(self, acc_details, transaction=None):
        if acc_details in self.account_repository.acc.keys():
            self.account_repository.acc[acc_details]['Transactions'].append(transaction)
        else:
            self.account_repository.acc[acc_details] = {"Transactions":[]}
   
    # This method will fetch the account details for an account Id, also reference is fetch to be able to reuse this.
    # However in the production view method will be different and wont be having reference details.
    def find_account_by_id(self, acc_id):
        for i in self.account_repository.acc.keys():
            if i.account_id == acc_id:
                return {'Account Id': i.account_id, 
                'Customer Id': i.customer_id,
                'Account number': i.account_number,
                'Balance': i.balance,
                'Account ref': i}

    # This method will fetch the account details of all accounts for an customer, also reference is fetch to be able to reuse this.
    # However in the production view method will be different and wont be having reference details.
    def find_accounts_by_customer_id(self, cust_id):
        acc_list = []
        for i in self.account_repository.acc.keys():
            if i.customer_id == cust_id:
                acc_list.append({'Account Id': i.account_id, 
                'Customer Id': i.customer_id,
                'Account number': i.account_number,
                'Balance': i.balance,
                'Account ref': i})
        
        return acc_list
      

# Class Customer      
class Customer:

    cust = {}

    def __init__(self, customer_id, name, email, phone_number):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.phone_number = phone_number
        Customer.cust[self.customer_id] = {"Name": self.name, "Email": self.email, "Contact": self.phone_number}



# Class transaction 
class Transactions:
    def __init__(self):
        self.account_repository = AccountRepository()
        
    # This method will create a customer and an account for the customer.
    # Also it will save the account details in AccountRepository.
    def create_account(self, customer_id, name, email, phone_number):
        Customer(customer_id, name, email, phone_number)
        acc_details = Account(customer_id)
        self.account_repository.save_account(acc_details)
        return self.account_repository.find_account_by_id(acc_details.account_id)
    
    # This method will make the transaction (Deposit or Withdraw) and save the transaction in AccountRepository
    def make_transaction(self, account_id, amount, tansaction_type):
        
        semaphore_transaction = Semaphore(1) # Using semaphore to make sure the transaction are mutually exclusive to maintain Atomicity.  
        semaphore_transaction.acquire() # Start of Semaphore

        acc = self.account_repository.find_account_by_id(account_id)
        curr_time = datetime.now()

        if tansaction_type.lower() == 'deposit':
            bal = acc['Account ref'].deposit(amount)
            transaction={'TimeStamp':str(curr_time),'Deposit': amount, 'Balance': acc['Account ref'].get_balance()}
            self.account_repository.save_account(acc['Account ref'], transaction)
        elif tansaction_type.lower() == 'withdraw':
            bal = acc['Account ref'].withdraw(amount)
            if bal > 0:
                transaction={'TimeStamp':str(curr_time),'Withdraw': amount, 'Balance': acc['Account ref'].get_balance()}
                self.account_repository.save_account(acc['Account ref'], transaction)
            else:
                transaction={'TimeStamp':str(curr_time),'Withdraw': amount, 'Balance':  acc['Account ref'].get_balance(), "Message": "Error: Withdraw amount is greater than Balance."}
        else:
            transaction={'TimeStamp':str(curr_time), 'Balance':  acc['Account ref'].get_balance(), "Message": "Error: Invalid Transaction type"}
        semaphore_transaction.release() # End of Semaphore
        
        return transaction
    
    # This method will fetch the transaction history from the AccountRepository
    def generate_account_statement(self, account_id):
        acc1 = self.account_repository.find_account_by_id(account_id)
        return self.account_repository.acc[acc1['Account ref']]
    

# Example

transaction = Transactions()
account_repository = AccountRepository()

# 1. Creating Accounts: 

# Creating account for customer
acc11 = transaction.create_account(1, 'Sam', 'sam@gmail.com', '9876543210')
print(acc11)

# Creating 3 accounts for 1 customer John
acc21 = transaction.create_account(2, 'John', 'John@gmail.com', '8886543210')
print(acc21)
acc22 = transaction.create_account(2, 'John', 'John@gmail.com', '8886543210')
print(acc22)
acc23 = transaction.create_account(2, 'John', 'John@gmail.com', '8886543210')
print(acc23)

# Creating 1 account for customer Rohit
acc31 = transaction.create_account(4, 'Rohit', 'Rohit@gmail.com', '7776543210')
print(acc31)

# Here Each will have a unique Account Id (to be used everywhere) and squencial Account number


# 2. Making Transaction in accounts

# Deposit money in Sam's account twice
t111 = transaction.make_transaction(acc11['Account Id'], 100, "Deposit")
print(t111)

t112 = transaction.make_transaction(acc11['Account Id'], 800, "Deposit")
print(t112)

# Deposit money in John's first two accounts
t211 = transaction.make_transaction(acc21['Account Id'], 300, "Deposit")
print(t211)
t221 = transaction.make_transaction(acc22['Account Id'], 200, "Deposit")
print(t221)

# Withdrawing Money from John's third account (getting error message)
t231 = transaction.make_transaction(acc23['Account Id'], 200, "Withdraw")
print(t231)

# Deposit Money from Rohit's account Twice and withdraw it once
t311 = transaction.make_transaction(acc31['Account Id'], 200, "Deposit")
print(t311)

t312 = transaction.make_transaction(acc31['Account Id'], 100, "Deposit")
print(t312)

t313 = transaction.make_transaction(acc31['Account Id'], 150, "Withdraw")
print(t313)


# 3. Checking the Statements

# Check Transaction History statements for all accounts.

s11 = transaction.generate_account_statement(acc11['Account Id'])
print(s11)

s21 = transaction.generate_account_statement(acc21['Account Id'])
print(s21)

s22 = transaction.generate_account_statement(acc22['Account Id'])
print(s22)

s23 = transaction.generate_account_statement(acc23['Account Id'])
print(s23)

s31 = transaction.generate_account_statement(acc31['Account Id'])
print(s31)


# 4. Fetching the details by Account Id and Customer Id

# Get account details by Account Id
r11 = account_repository.find_account_by_id(acc11['Account Id'])
print(r11)

r21 = account_repository.find_account_by_id(acc21['Account Id'])
print(r21)

r22 = account_repository.find_account_by_id(acc22['Account Id'])
print(r22)

r23 = account_repository.find_account_by_id(acc23['Account Id'])
print(r23)

r31 = account_repository.find_account_by_id(acc31['Account Id'])
print(r31)


# Get all accounts details by Customer Id
r1 = account_repository.find_accounts_by_customer_id(1)
print(r1)

r2 = account_repository.find_accounts_by_customer_id(2)
print(r2)

r3 = account_repository.find_accounts_by_customer_id(4)
print(r3)


# Note:
# Also reference to instance is there to be able to reuse the methods.
# However in the production view method will be different and wont be having reference details.
