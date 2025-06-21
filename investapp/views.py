from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Investment
import requests

# Homepage
def index(request):
    return render(request, 'investapp/index.html')

# Sign Up
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
        else:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect('dashboard')
    return render(request, 'investapp/signup.html')

# Login
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'investapp/login.html')

# Logout
def logout_view(request):
    logout(request)
    return redirect('home')

# Get BTC price
def get_btc_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    try:
        response = requests.get(url)
        data = response.json()
        return data['bitcoin']['usd']
    except:
        return 0  # fallback

# Dashboard
@login_required(login_url='login')
def dashboard(request):
    user = request.user
    btc_price = get_btc_price()
    investments = Investment.objects.filter(user=user)

    total_usd = sum(inv.current_value() for inv in investments if inv.confirmed)
    total_btc = sum(inv.btc_amount() for inv in investments if inv.confirmed)

    return render(request, 'investapp/dashboard.html', {
        'user': user,
        'btc_price': btc_price,
        'total_usd': total_usd,
        'total_btc': total_btc,
        'investments': investments
    })

# Make an Investment
@csrf_exempt
@login_required(login_url='login')
def invest(request):
    if request.method == "POST":
        amount = float(request.POST.get('amount'))
        btc_price = get_btc_price()

        investment = Investment.objects.create(
            user=request.user,
            amount_usd=amount,
            btc_rate=btc_price,
            confirmed=False  # wait for manual confirmation
        )
        return redirect('deposit', inv_id=investment.id)

# Deposit page
@login_required(login_url='login')
def deposit(request, inv_id):
    try:
        investment = Investment.objects.get(id=inv_id, user=request.user)
    except Investment.DoesNotExist:
        return redirect('dashboard')

    btc_amount = investment.btc_amount()
    btc_wallet = "bc1qxyz...demo_wallet"  # Replace with real BTC address

    return render(request, 'investapp/deposit.html', {
        'inv_id': investment.id,
        'btc_amount': btc_amount,
        'btc_wallet': btc_wallet
    })

# Withdraw page
@login_required(login_url='login')
def withdraw(request):
    user = request.user
    eligible_investments = Investment.objects.filter(user=user, confirmed=True)

    withdrawable = [inv for inv in eligible_investments if inv.can_withdraw()]
    total_withdrawable = sum(inv.current_value() for inv in withdrawable)

    return render(request, 'investapp/withdraw.html', {
        'withdrawable': withdrawable,
        'total': total_withdrawable
    })
from django.shortcuts import get_object_or_404

@login_required(login_url='login')
def confirm_deposit(request, inv_id):
    try:
        investment = Investment.objects.get(id=inv_id, user=request.user)
        investment.confirmed = True
        investment.save()
        return redirect('dashboard')
    except Investment.DoesNotExist:
        return redirect('dashboard')
