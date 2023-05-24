from django.urls import path
from . import views
from .views import StockListView, PortfolioListView, PortfolioDetailView, PortfolioStockListView, StockTransactionListView


urlpatterns = [
    path("", views.index, name="index"),
    path('stocks/', StockListView.as_view(), name='stock_list'),
    path('portfolios/', PortfolioListView.as_view(), name='portfolio_list'),
    path('portfolios/<int:pk>/', PortfolioDetailView.as_view(), name='portfolio_detail'),
]
