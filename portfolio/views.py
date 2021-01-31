from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.mail import EmailMessage
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import get_template
from django.urls import reverse
from django.db.models import Sum
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .fusioncharts import FusionCharts
from .serializers import CustomerSerializer
from decimal import Decimal
from .models import *
from .forms import *
from .utils import render_to_pdf
from django.views.decorators.cache import cache_page
now = timezone.now()


def home(request):
    return render(request, 'portfolio/home.html',
                 {'portfolio': home})


@login_required
def customer_list(request):
    customers = Customer.objects.filter(created_date__lte=timezone.now())
    return render(request, 'portfolio/customer_list.html',{'customers': customers})


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


@login_required
def portfolio(request,pk):
    customer = get_object_or_404(Customer, pk=pk)
    customers = Customer.objects.filter(created_date__lte=timezone.now())
    investments = Investment.objects.filter(customer=pk)
    stocks = Stock.objects.filter(customer=pk)
    sum_recent_value = Investment.objects.filter(customer=pk).aggregate(Sum('recent_value'))
    #print("sum_recent_value: " + str(sum_recent_value))
    #print(type(sum_recent_value))
    sum_acquired_value = Investment.objects.filter(customer=pk).aggregate(Sum('acquired_value'))
    #print("sum_acquired_value: " + str(sum_acquired_value))
    #print(type(sum_acquired_value))
    #overall_investment_results = sum_recent_value - sum_acquired_value--it is not working unsupported dict operands
    #overall_investment_results = sum_recent_value['recent_value__sum'] - sum_acquired_value['acquired_value__sum']
    overall_investment_results = Decimal(sum_recent_value.get('recent_value__sum')) - Decimal(sum_acquired_value.get('acquired_value__sum'))
    print("overall_investment_results:",overall_investment_results)
    #print("overall_investment_results1:", overall_investment_results1)
    # overall_investment_results = Decimal(sum_recent_value['recent_value__sum']) - Decimal(sum_acquired_value['acquired_value__sum'])
    #print(" overall_investment_results:" + str(overall_investment_results))

    # Initialize the value of the stocks
    sum_current_stocks_value = 0
    sum_of_initial_stock_value = 0

    # Loop through each stock and add the value to the total
    for stock in stocks:
        sum_current_stocks_value += stock.current_stock_value()
        #print(type((stock.current_stock_value())))
        #print(sum_current_stocks_value)
        #print("sum_current_stocks_value " + str(sum_current_stocks_value))
        sum_of_initial_stock_value += stock.initial_stock_value()
        #print(type((stock.initial_stock_value())))
        #print(sum_of_initial_stock_value)
        #print("sum_of_initial_stock_value " + str(sum_of_initial_stock_value))

    #overall_stocks_results = sum_current_stocks_value - sum_of_initial_stock_value
    # unsupported operand type(s) for -: 'float' and 'decimal.Decimal' for this line
    #overall_stocks_results = Decimal(sum_current_stocks_value) - Decimal(sum_of_initial_stock_value)
    overall_stocks_results = float(sum_current_stocks_value) - float(sum_of_initial_stock_value)
    #print(type(overall_stocks_results))
    #print("overall_stocks_results" + str(overall_stocks_results))
    return render(request, 'portfolio/portfolio.html', {'customer': customer,'investments': investments,
                                                        'stocks': stocks,
                                                        'sum_acquired_value': sum_acquired_value,
                                                        'sum_recent_value': sum_recent_value,
                                                        'sum_current_stocks_value': sum_current_stocks_value,
                                                        'sum_of_initial_stock_value': sum_of_initial_stock_value,
                                                        'overall_stocks_results': overall_stocks_results,
                                                        'overall_investment_results':overall_investment_results})


# List at the end of the views.py
# Lists all customers
class CustomerList(APIView):
    def get(self,request):
        customers_json = Customer.objects.all()
        serializer = CustomerSerializer(customers_json, many=True)
        return Response(serializer.data)


def downloadpdf(request,pk):
    customer = get_object_or_404(Customer, pk=pk)
    print("customer",customer);
    investments = Investment.objects.filter(customer=customer)
    print("investmnets",investments)
    stocks = Stock.objects.filter(customer=customer)
    sum_recent_value = Investment.objects.filter(customer=customer).aggregate(Sum('recent_value'))
    print("sum_recent_value: " + str(sum_recent_value))
    #print(type(sum_recent_value))
    sum_acquired_value = Investment.objects.filter(customer=customer).aggregate(Sum('acquired_value'))
    #print("sum_acquired_value: " + str(sum_acquired_value))
    #print(type(sum_acquired_value))
    overall_investment_results = sum_recent_value['recent_value__sum'] - sum_acquired_value['acquired_value__sum']
    #print(" overall_investment_results:" + str(overall_investment_results))
    # Initialize the value of the stocks
    sum_current_stocks_value = 0
    sum_of_initial_stock_value = 0

    # Loop through each stock and add the value to the total
    for stock in stocks:
        sum_current_stocks_value += stock.current_stock_value()
        #print(type((stock.current_stock_value())))
        #print("sum_current_stocks_value " + str(sum_current_stocks_value))
        sum_of_initial_stock_value += stock.initial_stock_value()
        #print(type(stock.initial_stock_value()))
        #print("sum_of_initial_stock_value " + str(sum_of_initial_stock_value))
        overall_stocks_results = float(sum_current_stocks_value) - float(sum_of_initial_stock_value)
        #print("overall_stocks_results" + str(overall_stocks_results))

    context = {
        'customer': customer, 'investments': investments,'stocks': stocks, 'sum_acquired_value': sum_acquired_value,
        'sum_recent_value': sum_recent_value, 'sum_current_stocks_value': sum_current_stocks_value,
        'sum_of_initial_stock_value': sum_of_initial_stock_value,
        'overall_stocks_results': overall_stocks_results,
        'overall_investment_results':overall_investment_results
            }

    #template = get_template('portfolio/portfolio_pdf.html')

    #html = template.render(context)

    pdf = render_to_pdf('portfolio/portfolio_pdf.html', context)

    #return HttpResponse(pdf,content_type='application/pdf')
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        customername = str(customer.name)
        print(customername)
        customername1 = customername.replace(" ", "_")
        print(customername1)
        filename = 'Portfolio_' + str(customername1) + '.pdf'
        content = "inline; filename=%s" % filename
        download = request.GET.get("download")
        if download:
            content = "attachment; filename=%s" % filename
        response['Content-Disposition'] = content
        return response
    return HttpResponseNotFound("not found")


def summarygraph(request, pk):
    investments = Investment.objects.filter(customer=pk)
    stocks = Stock.objects.filter(customer=pk)
    customer = get_object_or_404(Customer, pk=pk)
    dataSource = {'chart': {
        "caption": "Stock Details",
        "subCaption": "EFS",
        "xAxisName": "Stock",
        "yAxisName": "Value (In USD)",
        "numberPrefix": "$",
        "theme": "fusion"
    }, 'categories': []}

    # The data for the chart should be in an array where each element of the array is a JSON object
    # having the `label` and `value` as key value pair.
    categories = {'category': []}

    for stock_name in stocks:
        category = {'label': stock_name.name}
        print(category)
        categories['category'].append(category)

    dataSource['categories'].append(categories)
    dataSource['dataset'] = []
    seriesname = {'seriesname': 'Initial value', 'data': []}
    for key in stocks:
        data = {'value': float(key.initial_stock_value())}
        # data['label'] = key.name
        seriesname['data'].append(data)

    dataSource['dataset'].append(seriesname)

    seriesname_1 = {'seriesname': 'Current value', 'data': []}
    for key in stocks:
        data = {'value': float(key.current_stock_value())}
        # data['label'] = key.name
        seriesname_1['data'].append(data)

    dataSource['dataset'].append(seriesname_1)

    print('datasource', str(dataSource))

    dataSource_1 = {'chart': {
        "caption": "Investment Details",
        "subCaption": "EFS",
        "xAxisName": "Investment",
        "yAxisName": "Value (In USD)",
        "numberPrefix": "$",
        "theme": "fusion"
    }, 'categories': []}

    # The data for the chart should be in an array where each element of the array is a JSON object
    # having the `label` and `value` as key value pair.
    categories = {'category': []}

    for invest_name in investments:
        category = {'label': invest_name.category}
        categories['category'].append(category)

    dataSource_1['categories'].append(categories)
    dataSource_1['dataset'] = []
    seriesname = {'seriesname': 'Acquired value', 'data': []}
    for key in investments:
        data = {'value': float(key.acquired_value)}
        # data['label'] = key.name
        seriesname['data'].append(data)

    dataSource_1['dataset'].append(seriesname)

    seriesname_1 = {'seriesname': 'Recent value', 'data': []}
    for key in investments:
        data = {}
        # data['label'] = key.name
        data['value'] = float(key.recent_value)
        seriesname_1['data'].append(data)

    dataSource_1['dataset'].append(seriesname_1)

    print('dataSource_1', str(dataSource_1))

    sum_current_stocks_value = 0
    sum_of_initial_stock_value = 0
    for stock in stocks:
        # print('1...', stock.result_by_stock(stock.current_stock_value(), stock.initial_stock_value()))
        sum_current_stocks_value += stock.current_stock_value()
        sum_of_initial_stock_value += stock.initial_stock_value()

    total_stock_result = round((float(sum_current_stocks_value) - float(sum_of_initial_stock_value)), 2)
    sum_acquired_value = Investment.objects.filter(customer=pk).aggregate(Sum('acquired_value')).get(
        'acquired_value__sum', 0.00)
    sum_recent_value = Investment.objects.filter(customer=pk).aggregate(Sum('recent_value')).get('recent_value__sum',
                                                                                                 0.00)
    total_invest_result = sum_recent_value - sum_acquired_value
    portfolio_result = float(total_invest_result) + float(total_stock_result)

    dataSource_2 = {
        "chart": {
            "caption": "Split of portfolio result by stock and investment",
            "subCaption": "",
            "numberPrefix": "$",
            "showPercentInTooltip": "0",
            "decimals": "1",
            "useDataPlotColorForLabels": "1",
            "theme": "fusion"
        },
        "data": [
            {
                "label": "Stock",
                "value": float(total_stock_result)
            },
            {
                "label": "Investment",
                "value": float(total_invest_result)
            }
        ]
    }
    print('dataSource_2', str(dataSource_2))
    # Create an object for the Column 2D chart using the FusionCharts class constructor
    # column2D = FusionCharts("column2D", "ex1" , "600", "350", "chart-1", "json", dataSource)
    mscolumn2d = FusionCharts("mscolumn2d", "ex1", "600", "350", "chart-1", "json", dataSource)
    viewchart2 = FusionCharts("mscolumn2d", "ex2", "600", "350", "chart-2", "json", dataSource_1)
    viewchart3 = FusionCharts("pie2d", "chart-container", "550", "350", "chart-3", "json", dataSource_2)

    return render(request, 'portfolio/customer_summary.html', {'output': mscolumn2d.render(),
                                                               'output2': viewchart2.render(),
                                                               'output3': viewchart3.render(),
                                                               'customer': customer})


def email(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    print(customer)
    if request.method == "POST":
        form = EmailForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.published_date = timezone.now()
            post.save()
            emailto = request.POST.get('email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            document = request.FILES.get('document')
            print(document)
            email_from = 'djangotestformasters@gmail.com'
            recipient_list = [emailto]
            emailtosend = EmailMessage(subject, message, email_from, recipient_list)
            base_dir = 'media/documents'
            emailtosend.attach_file('media/documents/'+str(document))
            emailtosend.send()
            return render(request, 'portfolio/sent.html')
    else:
        #form = EmailForm(initial={'email': customer.email})
        form = EmailForm()
    return render(request, 'portfolio/email.html', {'emailform': form})
