from django.db import models
from django.utils.timezone import now


# Create your models here.

# <HINT> Create a Car Make model `class CarMake(models.Model)`:
# - Name
# - Description
# - Any other fields you would like to include in car make model
# - __str__ method to print a car make object
class CarMake(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=255)
    def __str__(self):
        return self.name
    

# <HINT> Create a Car Model model `class CarModel(models.Model):`:
# - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
# - Name
# - Dealer id, used to refer a dealer created in cloudant database
# - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
# - Year (DateField)
# - Any other fields you would like to include in car model
# - __str__ method to print a car make object
class CarModel(models.Model):
    SEDAN = 'Sedan'
    SUV = 'SUV'
    WAGON = 'Wagon'
    MINIVAN = 'Mini Van'
    MODEL_TYPES = [
        (SEDAN, 'Sedan'),
        (SUV, 'SUV'),
        (WAGON, 'Wagon'),
        (MINIVAN, 'Mini Van')
    ]
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    name = models.CharField(max_length=10)
    dealer_id = models.IntegerField(default=0)
    type = models.CharField(max_length=10, choices=MODEL_TYPES, default=SEDAN)
    year = models.IntegerField(default=0) #models.DateField(null=True, input_formats=['%Y'])
    def __str__(self):
        return self.name

# <HINT> Create a plain Python class `CarDealer` to hold dealer data
class CarDealer:
    id = None
    city = None
    state = None
    st = None
    address = None
    zip = None
    lat = None
    long = None
    short_name = None
    full_name = None

# <HINT> Create a plain Python class `DealerReview` to hold review data
class DealerReview:
    id = None
    name = None
    dealership = None
    review = None
    purchase = None
    purchase_date = None
    car_make = None
    car_model = None
    car_year = None
