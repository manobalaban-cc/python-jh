import datetime
import random
import csv

def generate_transaction_log(num_transactions=1000, filename="transactions.csv"):
  """Generates a transaction log with the specified number of transactions and saves it to a CSV file.

  Args:
    num_transactions: The number of transactions to generate.
    filename: The name of the CSV file to save the transactions.
  """

  currencies = ["USD", "EUR", "GBP", "JPY", "CAD"]
  recipients = ["Amazon", "Netflix", "Spotify", "Starbucks", "Uber"]

  transactions = []
  for _ in range(num_transactions):
    timestamp = datetime.datetime.now() + datetime.timedelta(days=random.randint(-365, 365))
    amount = round(random.uniform(10, 1000), 2)
    currency = random.choice(currencies)
    recipient = random.choice(recipients)
    transactions.append((timestamp, amount, currency, recipient))

  # Write transactions to CSV
  with open(filename, 'w', newline='') as csvfile:
    fieldnames = ['Timestamp', 'Amount', 'Currency', 'Recipient']
    writer = csv.writer(csvfile)
    writer.writerow(fieldnames)
    writer.writerows(transactions)

# Generate and save the transaction log
generate_transaction_log()