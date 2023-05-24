from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Stock(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=50)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    def __str__(self):
        return self.name + ' - ' + self.symbol
    

class Portfolio(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    stocks = models.ManyToManyField("Stock", through='PortfolioStock')

    def count_portfolio(self):
        portfolio_count = self.stocks.count()
        return portfolio_count
    
    @property
    def value(self):
        total_value = 0
        for portfolio_stock in self.portfoliostock_set.all():
            total_value += portfolio_stock.stock.current_price * portfolio_stock.quantity
        return total_value

    def __str__(self):
        return f"Portfolio owned by {self.owner}. Total Value: {self.value}"

    

class PortfolioStock(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    def __str__(self):
        return f'{self.stock.name} in {self.portfolio.name} - Quantity: {self.quantity}, Purchase Price: {self.purchase_price}'



class StockTransaction(models.Model):
    TRANSACTION_CHOICES = (
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    )

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    transaction_date = models.DateTimeField(default = datetime.now, blank= True)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_CHOICES)

    def __str__(self):
        return f'Transaction for {self.stock.name} - Quantity: {self.quantity}, Price: {self.price}, Date: {self.transaction_date}, Type: {self.get_transaction_type_display()}'

