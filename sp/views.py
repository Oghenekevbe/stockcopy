from django.http import HttpResponse, JsonResponse,HttpResponseRedirect,HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from .models import Stock, Portfolio, StockTransaction
from matplotlib.figure import Figure
import io
from .forms import RegistrationForm, ForgotPasswordForm, ResetPasswordForm, ChangePasswordForm, StockTransactionForm
from django.forms.models import model_to_dict
from decimal import Decimal
import json
from datetime import datetime
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import authenticate #, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin





# for email confirmation
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.contrib import messages
from django.contrib.auth import get_user_model




# Create your views here.

def index(request):
    
    return render(request,'index.html')

class StockListView(ListView):
    model = Stock
    template_name = 'stock_list.html'
    context_object_name = 'stocks'

class PortfolioListView(LoginRequiredMixin,ListView):
    model = Portfolio
    template_name = 'portfolio_list.html'
    context_object_name = 'portfolios'

    def get_context_data(self, **kwargs):
        if self.request.user.is_superuser:
            portfolios = Portfolio.objects.all()
        else:
            portfolios = Portfolio.objects.filter(owner=self.request.user)

        context = super().get_context_data(**kwargs)
        context["portfolios"] = portfolios
        return context



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



class PortfolioDetailView(LoginRequiredMixin,DetailView):
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

class StockTransactionView(LoginRequiredMixin,CreateView):
    form_class = StockTransactionForm
    template_name = 'perform_stock_transaction.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            portfolio = Portfolio.objects.get(owner=request.user)
            transaction.portfolio = portfolio
            transaction.save()
            return redirect('portfolio_list')  # Redirect to the portfolio page or any other appropriate page

        return render(request, self.template_name, {'form': form})




    #USER CREDENTIALS

# View for user registration
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            return redirect('index')

        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = RegistrationForm()

    return render(
        request=request,
        template_name="registration/register.html",
        context={"form": form}
        )

def activateEmail(request, user, to_email):
    mail_subject = 'Activate your user account.'
    message = render_to_string('registration/activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear {user}, please go to you email {to_email} inbox and click on the received activation link to confirm and complete the registration. If not found, kindly check your spam folder.')
    else:
        messages.error(request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated!')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid or has expired.')
        return redirect('index')
    

# Change password view
@login_required
def change_password(request):
    user = request.user
    if request.method == 'POST':
        form = ChangePasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = ChangePasswordForm(user)
    return render(request, 'registration/change_password.html', {'form': form})



# Forgot password view
def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            User = get_user_model()
            user = User.objects.filter(email=email).first()
            if user:
                # Perform password reset steps (e.g., send reset password email)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = account_activation_token.make_token(user)
                reset_link = f"{get_current_site(request)}/reset_password/{uid}/{token}/"
                message = render_to_string('registration/reset_password_email.html', {
                    'user': user,
                    'reset_link': reset_link,
                })
                email = EmailMessage(
                    subject='Reset Password',
                    body=message,
                    to=[user.email]
                )
                email.send()
                messages.success(request, 'An email with instructions to reset your password has been sent.')
                return redirect('index')
            else:
                messages.error(request, 'The email address provided is not associated with any user account.')
    else:
        form = ForgotPasswordForm()
    return render(request, 'registration/forgot_password.html', {'form': form})





# Reset password view
def reset_password(request, uidb64, token):
    print(f"uidb64: {uidb64}, token: {token}")  # Debugging statement
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
        print(user.email)
        print(user.username)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        return HttpResponseBadRequest("Invalid reset password link.")

    if account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = ResetPasswordForm(user=user, data=request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password1']
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Your password has been successfully reset. Kindly enter your new credentials to login')
                return redirect('login')  # Replace with your success URL
        else:
            form = ResetPasswordForm(user=user)
        return render(request, 'registration/reset_password.html', {'form': form})
    else:
        return HttpResponseBadRequest("Invalid reset password link.")
    


def reset_password_email(request):
    return render (request , 'reset-password_email.html')