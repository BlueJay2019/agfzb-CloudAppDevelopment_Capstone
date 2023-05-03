import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, SentimentOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    response = None
    try:
        #Call get method of requests library with URL and parameters
        api_key = kwargs.get("api_key")
        print("api_key : {}".format(api_key))
        if api_key:
            print("params : {}".format(kwargs['params']))
            response = requests.get(url, headers={'Content-Type': 'application/json'},params=kwargs['params'], 
                                        auth=HTTPBasicAuth('apikey', api_key))        
        else:
            print("Here?")
            response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)

        status_code = response.status_code
        print("With status {}".format(status_code))
        json_data = json.loads(response.text)
        return json_data

    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        return ""

 
# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    response = None
    try:
        response = requests.post(url,json=json_payload, params=kwargs)

        status_code = response.status_code
        print("With status {}".format(status_code))
        json_data = json.loads(response.text)
        return json_data

    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        return ""


# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
    results=[]
    state = kwargs.get("state")
    dealerId = kwargs.get("dealerId")

    if state:
        json_result = get_request(url, state=state)
    elif dealerId:
        json_result = get_request(url, dealerId=dealerId)
    else:
        json_result = get_request(url)

    if json_result:
        print(json_result)
        statusCode = json_result["statusCode"]
        if statusCode == 200:
            # Get the row list in JSON as dealers
            dealers = json_result["body"]
            # For each dealer object
            for dealer in dealers:
                # Get its content in `doc` object
                #dealer_doc = dealer["doc"]
                #dealer_doc = dealer
                # Create a CarDealer object with values in `doc` object
                dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                    id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                    short_name=dealer["short_name"],
                                    st=dealer["st"], zip=dealer["zip"])
                results.append(dealer_obj)
    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
#def get_dealer_reviews_from_cf(url, dealerId, **kwargs):
def get_dealer_reviews_from_cf(url, dealerId, **kwargs):
    results=[]
    print(kwargs)

    if dealerId:
        json_result = get_request(url, dealerId=dealerId)
    else:
        json_result = get_request(url)

    if json_result:
        print(json_result)
        statusCode = json_result["statusCode"]
        if statusCode == 200:
            # Get the row list in JSON as dealers
            reviews = json_result["body"]
            # For each dealer object
            for review in reviews:
                # Create a DealerReview object with values in `doc` object
                review_obj = DealerReview(
                    dealership = review['dealership'],
                    name = review['name'],
                    purchase =  review['purchase'] if 'purchase' in review else False,
                    review = review['review'],
                    purchase_date = review['purchase_date'] if 'purchase_date' in review else '',
                    car_make = review['car_make'] if 'car_make' in review else '',
                    car_model = review['car_model'] if 'car_model' in review else '',
                    car_year = review['car_year']  if 'car_year' in review else '',
                    id = review['id'] if 'id' in review else 0,
                    sentiment = "")
                review_obj.sentiment = analyze_review_sentiments(review_obj.review)
                results.append(review_obj)
    return results



#def get_dealer_by_id_from_cf(url, dealerId):
def get_dealer_by_id_from_cf(dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
    kwargs = {
        'dealerId': dealerId,
    }   

    url = "https://us-east.functions.appdomain.cloud/api/v1/web/dc39df14-a934-4f07-b1c4-720b0a8ffcf4/dealership-package/get-dealership.json"

    
    return get_dealers_from_cf(url, **kwargs)

def get_dealer_name_by_id_from_cf(dealerId):
    response = get_dealer_by_id_from_cf(dealerId)
    if response and len(response) > 0:
        return response[0].full_name
    
    return ""


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
    api_key = '1PbSYR3C0cmXIpEAm8U7hXE6Kbs3QNs6PjJU7KG3I6Ms'
    url = 'https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/bcef0e31-ad39-4aba-9dd5-10e36f2fe03f'

    authenticator = IAMAuthenticator(api_key) 

    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator) 

    natural_language_understanding.set_service_url(url) 

    source_text = text + ' helohellohellohellohelohellohellohello'
    try:
        response = natural_language_understanding.analyze( text=source_text,features=Features(sentiment=SentimentOptions(targets=[source_text]))).get_result() 

        label=json.dumps(response, indent=2) 
        print("label = {}".format(label))
        
        label = response['sentiment']['document']['label'] 
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        return "neutral"
    
    return(label) 

"""
    params = dict()
    params['text'] = text
    params['version'] = '2022-04-07'
    kwargs = {
        'api_key': api_key,
        'params': params
    }
    json_result = get_request(url, **kwargs)
    if json_result:
        print(json_result)
        if json_result['code'] != 200:
            return None
        
        return json_result['feature']['sentiment']

    return None
"""

