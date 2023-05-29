from django.urls import path
from . import views
from .views import StockListView, PortfolioListView, PortfolioDetailView



urlpatterns = [
    path("", views.index, name="index"),
    path('stocks/', StockListView.as_view(), name='stock_list'),
    path('portfolios/', PortfolioListView.as_view(), name='portfolio_list'),
    path('portfolios/<int:pk>/', PortfolioDetailView.as_view(), name='portfolio_detail'),



    # USER CREDENTIALS
    path('register/', views.register, name='register'),
    path('verify/<str:token>/', views.verify, name='verify'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password/<str:token>/', views.reset_password, name='reset_password'),
    path('stock_transactions_api/', views.stock_transactions_api),

]
