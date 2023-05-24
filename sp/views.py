from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from .models import Stock, Portfolio, PortfolioStock, StockTransaction
from matplotlib.figure import Figure
import io



# Create your views here.

def index(request):
    return render(request,'index.html')

class StockListView(ListView):
    model = Stock
    template_name = 'stock_list.html'
    context_object_name = 'stocks'

class PortfolioListView(ListView):
    model = Portfolio
    template_name = 'portfolio_list.html'
    context_object_name = 'portfolios'



class PortfolioDetailView(DetailView):
    model = Portfolio
    template_name = 'portfolio_detail.html'
    context_object_name = 'portfolio'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve transaction values
        transactions = StockTransaction.objects.filter(portfolio=self.object).order_by('transaction_date')

        # Separate x and y values
        y_values = [transaction.profit_loss for transaction in transactions]
        x_values = [transaction.transaction_date for transaction in transactions]


        # Create the figure and plot the graph
        fig = Figure()
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        ax.plot(x_values, y_values)
        ax.set_xlabel('Transaction Date')
        ax.set_ylabel('Profit/Loss')
        ax.set_title('Transaction History')

        # Save the figure to a buffer
        buffer = io.BytesIO()
        canvas.print_png(buffer)
        context['transaction_history'] = buffer.getvalue()

        return context

class PortfolioStockListView(ListView):
    model = PortfolioStock
    template_name = 'portfolio_stock_list.html'
    context_object_name = 'stocks'

    def get_queryset(self):
        portfolio = get_object_or_404(Portfolio, id=self.kwargs['portfolio_id'])
        return portfolio.stocks.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['portfolio'] = get_object_or_404(Portfolio, id=self.kwargs['portfolio_id'])
        return context

