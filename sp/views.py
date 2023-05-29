from django.http import HttpResponse, JsonResponse,HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from .models import Stock, Portfolio, PortfolioStock, StockTransaction,VerificationModel
from matplotlib.figure import Figure
import io
from .forms import RegistrationForm, ForgotPasswordForm
from django.forms.models import model_to_dict
from decimal import Decimal
import json
from datetime import datetime
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt



# for email confirmation
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
import random



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

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


# def stock_transactions_api(request):
#     stock_transactions = StockTransaction.objects.all()
#     serialized_data = serializers.serialize('json', stock_transactions)
#     return JsonResponse(serialized_data, safe=False)


@csrf_exempt
def stock_transactions_api(request):
    if request.method == 'GET':
        # Retrieve existing stock transactions
        stock_transactions = StockTransaction.objects.all()

        # Serialize the stock transactions into JSON
        serialized_data = serializers.serialize('json', stock_transactions)
        return JsonResponse(serialized_data, safe=False)

    elif request.method == 'POST':
        stock_transactions = StockTransaction.objects.all()

        # Generate random values for transaction_type, stock, portfolio, quantity, price
        transaction_type = random.choice(['BUY', 'SELL'])
        stock_id = stock_transactions.stock.id  # Replace with the appropriate logic to get a random stock ID
        portfolio_id = stock_transactions.portfolio.id  # Replace with the appropriate logic to get a random portfolio ID
        quantity = random.randint(1, 100)
        price = round(random.uniform(1, 100), 2) 

        try:
            # Create a new StockTransaction object
            stock_transaction = StockTransaction(
                transaction_type=transaction_type,
                stock_id=stock_id,
                portfolio_id=portfolio_id,
                quantity=quantity,
                price=price
            )

            # Save the new transaction
            stock_transaction.save()

            return JsonResponse({'success': True, 'message': 'Transaction created successfully.'})
        except ValueError as e:
            # Error occurred while saving the transaction
            return JsonResponse({'success': False, 'message': str(e)})



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



#USER CREDENTIALS

# View for user registration
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            token = str(random.random()).split('.')[1]
            verification = VerificationModel.objects.create(user=user, token=token, is_verified=False)

            domain = get_current_site(request).domain
            verification_link = f'http://{domain}/verify/{token}'

            send_mail(
                'Email Verification',
                f'Please click the following link to verify your email: {verification_link}',
                'noreply@example.com',
                [user.email],
                fail_silently=False,
            )

            messages.success(request, 'A confirmation email has been sent to your email address.')
            return redirect('register')
    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def verify(request, token):
    try:
        verification = VerificationModel.objects.get(token=token)
        verification.is_verified = True
        verification.save()

        messages.success(request, 'Your email has been verified. You can now log in.')
        return redirect('login')

    except VerificationModel.DoesNotExist:
        messages.error(request, 'Your verification was not successful. Please try again.')
        return redirect('register')



def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Generate password reset token
            token = str(random.random()).split('.')[1] 

            # Save the token in the User model
            user.verfificationmodel.token = token
            user.verfificationmodel.save()

            # Construct reset password URL
            domain_name = get_current_site(request).domain
            reset_url = f'http://{domain_name}/reset_password/{token}/'

            # Send password reset email
            send_mail(
                'Password Reset',
                f'Click the following link to reset your password: {reset_url}',
                'NoReply@testing.com',
                [email],
                fail_silently=False,
            )

            return HttpResponse('A password reset link has been sent to your email address.')
        except User.DoesNotExist:
            message = 'Email does not exist in our system.'
            return render(request, 'registration/forgot_password.html', {'message': message})
    form = ForgotPasswordForm()
    return render(request, 'registration/forgot_password.html', {'form': form})


def reset_password(request, token):
    try:
        # Get CustomerProfile associated with the token
        customer_profile = VerificationModel.objects.get(token=token)

        # Check if token is valid
        if customer_profile.token == token:
            user = customer_profile.user
            if request.method == 'POST':
                # Perform password reset
                password = request.POST['password1']
                user.set_password(password)
                user.save()
                # Clear token in CustomerProfile model
                customer_profile.token = ''
                customer_profile.save()
                return redirect('login')
            return render(request, 'registration/reset_password.html', {'token': token, 'form': PasswordResetForm()})
        else:
            message = 'Invalid token. Please try again.'
            return render(request, 'index.html', {'message': message})
    except VerificationModel.DoesNotExist:
        message = 'Profile does not exist. Please try again.'
        return render(request, 'index.html', {'message': message})