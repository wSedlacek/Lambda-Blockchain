import requests

from sys import argv

if __name__ == '__main__':
    # What is the server address? IE `python3 miner.py https://server.com/api/`
    if len(argv) > 1:
        user_id = argv[1]
    else:
        user_id = input("What is your User ID? ")

    if len(argv) > 2:
        node = argv[2]
    else:
        node = "http://localhost:5000"

    try:
        transactions = requests.get(url=f"{node}/{user_id}/transactions")
        balance = requests.get(url=f"{node}/{user_id}/balance")
        try:
            transactions = transactions.json()
            balance = balance.json()
        except ValueError:
            print("Could not read data from the server...")

        print("Transactions.....")
        for transaction in transactions:
            print(transaction)
        print(f"Your balance is {balance}")

    except requests.exceptions.ConnectionError:
        pass
