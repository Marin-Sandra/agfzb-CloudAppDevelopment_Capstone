from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from .restapis import get_dealers_from_cf
from .restapis import get_dealer_by_id_from_cf
from .restapis import post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
# def about(request):
# ...
def get_about(request):
    if request.method == "GET":
        return render(request, 'djangoapp/about.html')


# Create a `contact` view to return a static contact page
#def contact(request):
def get_contact(request):
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
# def login_request(request):
# ...
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        print("username:",username)
        print("password:",password)
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            #return redirect('djangoapp/logined.html')
            #return render(request, 'djangoapp/logined.html', context)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            
            #return redirect('djangoapp/index.html')
            return redirect('djangoapp:index')
    

# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...
def logout_request(request):
    logout(request)
    #return render(request, 'djangoapp/logouted.html')
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
# def registration_request(request):
# ...

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
    if request.method == "GET":
        url = "https://f2d2e875.us-south.apigw.appdomain.cloud/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        #dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        #return HttpResponse(dealer_names)
        context = {"dealership_list": dealerships}
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...

def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "https://f2d2e875.us-south.apigw.appdomain.cloud/api/dealership"
        review=get_dealer_by_id_from_cf(url,dealer_id)

        #return HttpResponse(review)
        context = {"review_list": reviews,  "dealer_id": dealer_id}
        return render(request, 'djangoapp/dealer_details.html', context)



# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    user = request.user
        if request.method == "POST":
           if user.is_authenticated:
            review=dict()
            review["time"] = datetime.utcnow().isoformat()
            review["name"] = request.user.username
            review["dealership"] = dealer_id
            review["review"] = request.POST.get("content")
            review["purchase"] = False
            if "purchasecheck" in request.POST:
                if request.POST["purchasecheck"] == 'on':
                    review["purchase"] = True
            review["purchase_date"] = request.POST["purchasedate"]
            car_id = request.POST["car"]
            car = CarModel.car_manager.get(pk=car_id)
            review["car_make"] = car.make.name
            review["car_model"] = car.name
            review["car_year"] = int(car.year)
            jsonPayload = {"review": review}
            url="https://f2d2e875.us-south.apigw.appdomain.cloud/api/review"
            post_request(url, jsonPayload,dealer_id)
            return HttpResponse("OK")