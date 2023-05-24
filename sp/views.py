from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Stock, Portfolio, PortfolioStock, StockTransaction


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

class StockTransactionListView(ListView):
    model = StockTransaction
    template_name = 'stock_transaction_list.html'
    context_object_name = 'transactions'

