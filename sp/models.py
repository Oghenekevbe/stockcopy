from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal



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
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def count_portfolio(self):
        portfolio_count = self.stocks.count()
        return portfolio_count
    
    @property
    def value(self):
        total_value = 0
        for portfolio_stock in self.portfoliostock_set.all():
            total_value += float(str(portfolio_stock.stock.current_price)) * portfolio_stock.quantity
        return total_value

    def __str__(self):
        return f"Portfolio owned by {self.owner}. Total Value: N{self.value}. Wallet Balance N{self.wallet}"

    

class PortfolioStock(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    def __str__(self):
        return f'{self.stock.name} in {self.portfolio.name}, owned by {self.portfolio.owner} - Quantity: {self.quantity}, Purchase Price: {self.purchase_price}'


class StockTransaction(models.Model):
    TRANSACTION_CHOICES = (
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    )

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    transaction_date = models.DateTimeField(default=timezone.now, blank=True)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_CHOICES)

    def __str__(self):
        return f'Transaction for {self.portfolio.owner} - {self.stock.name} - Quantity: {self.quantity}, Price: {self.price}, Date: {self.transaction_date}, Type: {self.get_transaction_type_display()}'
    
    def save(self, *args, **kwargs):
        wallet_balance = Decimal(str(self.portfolio.wallet))  # Convert Decimal128 to decimal.Decimal

        if self.transaction_type == 'BUY' and self.price * self.quantity > wallet_balance:
            raise ValueError("Insufficient funds in the wallet to perform the transaction.")

        # Save the instance using the super method
        super().save(*args, **kwargs)

        if self.transaction_type == 'BUY':
            portfolio_stock = self.portfolio.portfoliostock_set.filter(stock=self.stock).first()
            if portfolio_stock:
                portfolio_stock.quantity += self.quantity
                portfolio_stock.save()
            else:
                PortfolioStock.objects.create(stock=self.stock, portfolio=self.portfolio, quantity=self.quantity)

            # Deduct transaction value from the wallet balance
            self.portfolio.wallet = Decimal(str(wallet_balance)) - (Decimal(str(self.price)) * Decimal(str(self.quantity)))
            self.portfolio.save()
        elif self.transaction_type == 'SELL':
            portfolio_stock = self.portfolio.portfoliostock_set.filter(stock=self.stock).first()
            if portfolio_stock:
                portfolio_stock.quantity -= self.quantity
                portfolio_stock.save()

            # Add transaction value to the wallet balance
            self.portfolio.wallet = Decimal(str(wallet_balance)) + (Decimal(str(self.price)) * Decimal(str(self.quantity)))
            self.portfolio.save()
        
        
    @property
    def profit_loss(self):
        current_value = Decimal(str(self.stock.current_price)) * Decimal(str(self.quantity))

        transaction_value = Decimal(str(self.price)) * Decimal(str(self.quantity))

        if self.transaction_type == 'BUY':
            if transaction_value > current_value:
                return current_value - transaction_value  # Loss
            else:
                return current_value - transaction_value  # Profit
        elif self.transaction_type == 'SELL':
            if transaction_value > current_value:
                return transaction_value - current_value  # Profit
            else:
                return transaction_value - current_value  # Loss
