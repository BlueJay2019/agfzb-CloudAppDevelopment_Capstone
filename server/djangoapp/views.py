from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarDealer, DealerReview, CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request, get_dealer_name_by_id_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    return render(request, 'djangoapp/about.html')


# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/index.html', context)
    else:
        context['message'] = "Invalid method"
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://us-east.functions.appdomain.cloud/api/v1/web/dc39df14-a934-4f07-b1c4-720b0a8ffcf4/dealership-package/get-dealership.json"
        # Get dealers from the URL
        dealer_list = get_dealers_from_cf(url)

        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealer_list])
        # Return a list of dealer short name
        print(dealer_names)
        context['dealer_names'] = dealer_names
        context['dealer_list'] = dealer_list
        
        return render(request, 'djangoapp/index.html', context)

    return render(request, 'djangoapp/index.html', status = 400)



# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, id):
    context = {}
    if request.method == "GET":
        url = "https://us-east.functions.appdomain.cloud/api/v1/web/dc39df14-a934-4f07-b1c4-720b0a8ffcf4/dealership-package/get-review.json"
        # Get dealers from the URL
        review_list = get_dealer_reviews_from_cf(url,id)

        #if len(review_list) == 0:
            #return get_dealerships(request) #redirect(request,'djangoapp:index')
        context['dealer_id'] = id
        context['dealer_name'] = get_dealer_name_by_id_from_cf(id)
        context['review_list'] = review_list
    
    return render(request, 'djangoapp/dealer_details.html', context)

    #return redirect(request,'djangoapp:index')


# Create a `add_review` view to submit a review
def add_review(request, id):
    context = {}
    context['dealer_id'] = id

    if request.method == "POST":
        url = "https://us-east.functions.appdomain.cloud/api/v1/web/dc39df14-a934-4f07-b1c4-720b0a8ffcf4/dealership-package/post-review.json"
        review = {}

        json_payload = {}
        review['name'] = request.user.first_name + ' ' + request.user.last_name
        review["time"] = datetime.utcnow().isoformat()
        review["dealership"] = id
        review["review"] = request.POST['review']
        #review["purchase"]= request.POST['purchace']
        checkbox_values = request.POST.getlist('purchase')
        review["purchase"] = True if len(checkbox_values) > 0 else False
        review["purchase_date"]= request.POST['purchase_date']
        car_id = request.POST['car']
        select_car = CarModel.objects.filter(dealer_id = id, id = car_id)
        if select_car:
            review["car_model"] = select_car[0].name
            review["car_make"] = select_car[0].car_make.name
            review["car_year"] = select_car[0].year

        json_payload["review"] = review
        result = post_request(url, json_payload)

        return redirect("djangoapp:dealer_details", id=id)
    else:
        car_list = CarModel.objects.filter(dealer_id = id)

        context['dealer_name'] = get_dealer_name_by_id_from_cf(id)
        context['car_list'] = car_list

    return render(request, 'djangoapp/add_review.html', context)