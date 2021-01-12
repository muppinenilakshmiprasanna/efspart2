from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from .models import *
from .forms import *


now = timezone.now()


def home(request):
    return render(request, 'portfolio/home.html',
                 {'portfolio': home})


@login_required
def customer_list(request):
    customer = Customer.objects.filter(created_date__lte=timezone.now())
    return render(request, 'portfolio/customer_list.html',{'customers': customer})


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        # update
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.updated_date = timezone.now()
            customer.save()
            #customer = Customer.objects.filter(created_date__lte=timezone.now())
            #return render('portfolio/customer_list.html',{'customers': customer})
            return redirect('portfolio:customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'portfolio/customer_edit.html', {'form': form})


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect('portfolio:customer_list')


@login_required
def customer_new(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.created_date = timezone.now()
            customer.save()
            customer = Customer.objects.filter(created_date__lte=timezone.now())
            #context= {'customers': customer}
            return redirect('portfolio:customer_list')
            #return redirect(reverse('portfolio:customer_list'),context)
            #return HttpResponseRedirect(reverse('portfolio:customer_list'), context)
    else:
        form = CustomerForm()
    return render(request, 'portfolio/customer_new.html', {'form': form})


@login_required
def stock_list(request):
    stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
    return render(request, 'portfolio/stock_list.html', {'stocks': stocks})


@login_required
def stock_new(request):
    if request.method == "POST":
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.created_date = timezone.now()
            stock.save()
            #stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
            #return render(request, 'portfolio/stock_list.html',{'stocks': stocks})
            return redirect('portfolio:stock_list')
    else:
        form = StockForm()
        # print("Else")
    return render(request, 'portfolio/stock_new.html', {'form': form})


@login_required
def stock_edit(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == "POST":
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            stock = form.save()
            # stock.customer = stock.id
            stock.updated_date = timezone.now()
            stock.save()
            #stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
            #return render(request, 'portfolio/stock_list.html', {'stocks': stocks})
            return redirect('portfolio:stock_list')
    else:
        # print("else")
        form = StockForm(instance=stock)
    return render(request, 'portfolio/stock_edit.html', {'form': form})


@login_required
def stock_delete(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    stock.delete()
    return redirect('portfolio:stock_list')


@login_required
def investment_list(request):
    investments = Investment.objects.filter(acquired_date__lte=timezone.now())
    return render(request, 'portfolio/investment_list.html', {'investments': investments})


@login_required
def investment_new(request):
    if request.method == "POST":
        form = InvestmentForm(request.POST)
        if form.is_valid():
            investment = form.save(commit=False)
            investment.created_date = timezone.now()
            investment.save()
            #stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
            #return render(request, 'portfolio/stock_list.html',{'stocks': stocks})
            return redirect('portfolio:investment_list')
    else:
        form = InvestmentForm()
        # print("Else")
    return render(request, 'portfolio/investment_new.html', {'form': form})


@login_required
def investment_edit(request, pk):
    investment = get_object_or_404(Investment, pk=pk)
    if request.method == "POST":
        form = InvestmentForm(request.POST, instance=investment)
        if form.is_valid():
            investment = form.save()
            # stock.customer = stock.id
            investment.updated_date = timezone.now()
            investment.save()
            #stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
            #return render(request, 'portfolio/stock_list.html', {'stocks': stocks})
            return redirect('portfolio:investment_list')
    else:
        # print("else")
        form = InvestmentForm(instance=investment)
    return render(request, 'portfolio/investment_edit.html', {'form': form})


@login_required
def investment_delete(request, pk):
    investment = get_object_or_404(Investment, pk=pk)
    investment.delete()
    return redirect('portfolio:investment_list')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            advisor_group = Group.objects.get_or_create(name='Advisor')
            advisor_group[0].user_set.add(user)
            return render(request,'registration/registerdone.html', {'form': form})
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})
