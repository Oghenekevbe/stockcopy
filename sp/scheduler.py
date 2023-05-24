import schedule
import time
import random
from datetime import datetime
from .models import StockTransaction, Stock, Portfolio


def create_transaction():
    stocks = Stock.objects.all()
    portfolios = Portfolio.objects.all()

    stock = random.choice(stocks)
    portfolio = random.choice(portfolios)
    transaction_type = random.choice(['BUY','SELL'])
    quantity = random.randint(1,10)
    price = random.randint(20,50)


    transaction = StockTransaction.objects.create(
    transaction_type=transaction_type,
    stock=stock,
    portfolio=portfolio,
    quantity=quantity,
    price=price,
    transaction_date=datetime.now()
)

    transaction.save()
    print('Transaction created:', transaction)

schedule.every(1).minutes.do(create_transaction)

while True:
    schedule.run_pending()
    time.sleep(1)