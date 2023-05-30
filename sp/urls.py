from django.urls import path
from . import views
from sp.views import StockListView, PortfolioListView, PortfolioDetailView,StockTransactionView



urlpatterns = [
    path("", views.index, name="index"),
    path('stocks/', StockListView.as_view(), name='stock_list'),
    path('perform_stock_transaction/', StockTransactionView.as_view(), name='perform_stock_transaction'),
    path('portfolios/', PortfolioListView.as_view(), name='portfolio_list'),
    path('portfolios/<int:pk>/', PortfolioDetailView.as_view(), name='portfolio_detail'),



    # USER CREDENTIALS
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('forgot_password/', views.forgot_password, name= 'forgot_password'),
    path('reset_password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('reset_password_email/', views.reset_password_email, name='reset_password_email'),
    path('change-password/', views.change_password, name='change_password'),            
    path('stock_transactions_api/', views.stock_transactions_api),

]
