from flask import Flask, request, jsonify, render_template
import datetime
from datetime import datetime
import pytz
import calendar
import os
import dialogflow
import requests
import json
from API.YelpFusion import YelpFusion, validate_params
from API.YelpRecommender import YelpRecommender, validate_params as val_params
from gcloud import storage
from PIL import Image
from os import listdir, path
import urllib.request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True)   # get the incoming JSON structure
    action = data['queryResult']['action'] # get the action name associated with the matched intent
    
    if (action == 'test_connection'):
        return test_connection(data)

    if(action == 'getBusiness'):
        return get_Business(data)
   
    if(action == 'searchBusiness'):
        return search_Business(data)

    if(action == 'searchBusinessByPhone'):
        return search_BusinessByPhone(data)

    if(action == 'searchFoodDeliveryBusinesses'):
        return search_FoodDeliveryBusinesses(data)

    if(action == 'matchBusiness'):
        return match_Business(data)

    if(action == 'getBusinessReviews'):
        return get_BusinessReviews(data)

    if(action == 'getRecommendations'):
        return get_Recommendations(data)

    if(action == 'getFeaturedEvents'):
        return get_FeaturedEvents(data)

def test_connection(data):
    reply = {}
    reply["fulfillmentText"] = "Yelper Assistant Connection Test Successful!"
    return jsonify(reply)
	
	
def get_Business(data):
    parameters = data['queryResult']['parameters']

    # validate request parameters, return an error if there are issues
    error, search_params = validate_params(parameters)
    if error:
        return error

    # create a YelpFusion object which retrieves the business details from YelpFusion API
    try:
        yelpFusion = YelpFusion(search_params)
        response = yelpFusion.getBusiness()
        if(response.get("error") is None):
            #generateImgMosaic(response['image_url'], response['photos'])
            #uploadImageToGCP(response['name'])
            contact = ", ".join(response["location"]["display_address"]) + " [" + response["display_phone"] + "]"
            #url = "https://storage.cloud.google.com/yelperassistant.appspot.com/images/{}.jpg".format(response['name'])
            #url = response['image_url']
            url = response['photos'][1]
            
            #day_map = {0:"Sun", 1:"Mon", 2:"Tue", 3:"Wed", 4:"Thu", 5:"Fri", 6:"Sat"}

            info = []
            operatinghrs_wkday = ""
            operatinghrs_wkend = ""
            hours = response.get("hours")
            if(hours is None):
                info = []
            else:
                operatinghrs_wkday = hours[0]['open'][1]['start'] + "-" + hours[0]['open'][1]['end']
                operatinghrs_wkend = hours[0]['open'][0]['start'] + "-" + hours[0]['open'][0]['end']
                #for times in hours[0]['open']:
                #    operatinghrs += day_map[times['day']] + ": " + times['start'] + "-" + times['end']
                info.append({
                                "text": "WkDay: " + operatinghrs_wkday,
                                "postback": ""
                })
                info.append({
                                "text": "WkEnd: " + operatinghrs_wkend,
                                "postback": ""
                })

            categories = response.get("categories")
            category_list = ", ".join([category["title"] for category in categories])
            info.append({
                "text": "Cat: " + category_list,
                "postback": ""
            })

            info.append({
                    "text": "Visit Yelp Page",
                    "postback": response["url"]
            })

            info.append({
                    "text": "Get Directions",
                    "postback": "https://www.yelp.com/map/" + response["alias"]
            })

            reply = build_Card_Msg(response['name'], contact, url, info)
        else:
            reply = build_Singleline_Msg(response["error"]['description'])
    # return an error if there is an error getting the forecast
    except (ValueError, IOError) as error:
        return error	   
   
    return jsonify(reply)

def search_Business(data):
    parameters = data['queryResult']['parameters']

    # validate request parameters, return an error if there are issues
    error, search_params = validate_params(parameters)
    if error:
        return error

    # create a YelpFusion object which retrieves the business details from YelpFusion API
    try:
        yelpFusion = YelpFusion(search_params)
        response = yelpFusion.searchBusiness()
        businesses = response.get('businesses')
        if(businesses is None):
            reply = build_Singleline_Msg("No matching businesses found")
        else:
            reply = build_MultiCard_Msg(businesses)
    # return an error if there is an error getting the forecast
    except (ValueError, IOError) as error:
        return error	   

    return jsonify(reply)

def search_BusinessByPhone(data):
    parameters = data['queryResult']['parameters']

    # validate request parameters, return an error if there are issues
    error, search_params = validate_params(parameters)
    if error:
        return error

    # create a YelpFusion object which retrieves the business details from YelpFusion API
    try:
        yelpFusion = YelpFusion(search_params)
        response = yelpFusion.searchBusinessByPhone()
        businesses = response.get('businesses')
        if(len(businesses) == 0):
            reply = build_Singleline_Msg("No matching businesses found")
        else:
            reply = build_MultiCard_Msg(businesses)
        #business_id = businesses[0]['name']
        #business_addr = businesses[0]['location']['address1']
    # return an error if there is an error getting the forecast
    except (ValueError, IOError) as error:
        return error	   
    
    return jsonify(reply)

def search_FoodDeliveryBusinesses(data):
    parameters = data['queryResult']['parameters']

    # validate request parameters, return an error if there are issues
    error, search_params = validate_params(parameters)
    if error:
        return error

    # create a YelpFusion object which retrieves the business details from YelpFusion API
    try:
        yelpFusion = YelpFusion(search_params)
        response = yelpFusion.searchFoodDeliveryBusinesses()
        businesses = response.get('businesses')
        if(len(businesses) == 0):
            reply = build_Singleline_Msg("No matching businesses found")
        else:
            reply = build_MultiCard_Msg(businesses)
    # return an error if there is an error getting the forecast
    except (ValueError, IOError) as error:
        return error	   
    
    return jsonify(reply)

def match_Business(data):
    parameters = data['queryResult']['parameters']

    # validate request parameters, return an error if there are issues
    error, search_params = validate_params(parameters)
    if error:
        return error

    # create a YelpFusion object which retrieves the business details from YelpFusion API
    try:
        yelpFusion = YelpFusion(search_params)
        response = yelpFusion.matchBusiness()

        reply = build_Multiline_Msg(response)
    # return an error if there is an error getting the forecast
    except (ValueError, IOError) as error:
        return error	   
    
    return jsonify(reply)

def get_BusinessReviews(data):
    parameters = data['queryResult']['parameters']

    # validate request parameters, return an error if there are issues
    error, search_params = validate_params(parameters)
    if error:
        return error

    # create a YelpFusion object which retrieves the business details from YelpFusion API
    try:
        yelpFusion = YelpFusion(search_params)
        response = yelpFusion.getBusinessReviews()
        reviews = response.get('reviews')
        if(len(reviews) == 0):
            reply = build_Singleline_Msg("No reviews found")
        else:
            reply = build_Multiline_Msg2(reviews)
    # return an error if there is an error getting the forecast
    except (ValueError, IOError) as error:
        return error	   

    return jsonify(reply)

def get_AutocompleteSuggestions(data):
    parameters = data['queryResult']['parameters']

    # validate request parameters, return an error if there are issues
    error, search_params = validate_params(parameters)
    if error:
        return error

    # create a YelpFusion object which retrieves the business details from YelpFusion API
    try:
        yelpFusion = YelpFusion(search_params)
        response = yelpFusion.getAutocompleteSuggestions()
        categories_list = response.get('categories')
        terms_list = response.get('terms')
    # return an error if there is an error getting the forecast
    except (ValueError, IOError) as error:
        return error	   
        
    reply = {}
    reply["fulfillmentText"] = categories_list
    reply["fulfillmentMessages"] = []

    return jsonify(reply)   

def get_Recommendations(data):
    parameters = data['queryResult']['parameters']

    # validate request parameters, return an error if there are issues
    error, search_params = val_params(parameters)
    if error:
        return error

    # create a YelpRecommender object which retrieves user recommendations from YelpRecommender API
    try:
        yelpRecommender = YelpRecommender(search_params)
        response = yelpRecommender.getReommendations()
        if type(response) == list:
            reply = build_MultiCard_Msg2(response)
        else:
            reply = build_Singleline_Msg("No recommendations found")
    # return an error if there is an error getting the forecast
    except (ValueError, IOError) as error:
        return error	   

    return jsonify(reply)

def get_FeaturedEvents(data):
    parameters = data['queryResult']['parameters']

    # validate request parameters, return an error if there are issues
    error, search_params = validate_params(parameters)
    if error:
        return error

    # create a YelpFusion object which retrieves the business details from YelpFusion API
    try:
        yelpFusion = YelpFusion(search_params)
        response = yelpFusion.getFeaturedEvents()

        info = []
        if response:
            address = ", ".join(response["location"]["display_address"])
            eventDate = datetime.strptime(response['time_start'].split("T")[0], '%Y-%m-%d')
            eventDate = eventDate.strftime('%d-%m-%Y')

            info.append({
                    "text": "Date: " + eventDate,
                    "postback": ""
            })

            info.append({
                    "text": "Get Tickets",
                    "postback": response['tickets_url']
            })

            info.append({
                    "text": "Visit event site",
                    "postback": response['event_site_url']
            })            

            reply = build_Card_Msg(response['name'], response['description'], response['image_url'], info)
        else:
            reply = build_Singleline_Msg("No featured events found")
    # return an error if there is an error getting the forecast
    except (ValueError, IOError) as error:
        return error	   
    
    return jsonify(reply)

def build_Singleline_Msg(content):
    reply = {
        "fulfillmentText": " " ,
        "fulfillmentMessages" : [
            {
              "text" : {
                  "text" : [content]
              }
              ,
              "platform": "SLACK"    
            },
            {
              "text" : {
                  "text" : [content]
              }
              ,
              "platform": "TELEGRAM"    
            },
            {
              "text" : {
                  "text" : [content]
              }   
            }
        ]
    }

    return reply

def build_Multiline_Msg(businesses):

    msgs = []
    for business in businesses:
        print(business)
        name = "Name: {}".format(business["name"])
        address = "Address: {}, {}, {}, {}".format(business["location"]["address1"], business["location"]["city"], business["location"]["state"], business["location"]["zip_code"])
        contact = "Contact: {}".format(business["phone"])
        line = [name, address, contact]
        response_slack = {'text': {'text': [line]}, "platform": "SLACK" }
        response_telegram = {'text': {'text': [line]}, "platform": "TELEGRAM" }
        response_default = {'text': {'text': [line]} }
        msgs.append(response_slack)
        msgs.append(response_telegram)
        msgs.append(response_default)
        
    reply = {}
    reply["fulfillmentText"] = " "
    reply["fulfillmentMessages"] = msgs    

    return reply

def build_Multiline_Msg2(reviews):
    msgs = []
    review_texts = []
    for i in range(len(reviews)):
        review_texts.append("Review #{}:".format(i+1))
        review_texts.append("-------------")
        review_texts.append(reviews[i]['text'])
        review_texts.append("")

    response_slack = {'text': {'text': review_texts}, "platform": "SLACK" }
    response_telegram = {'text': {'text': review_texts}, "platform": "TELEGRAM" }
    response_default = {'text': {'text': review_texts} }
    msgs.append(response_slack)
    msgs.append(response_telegram)
    msgs.append(response_default)
        
    reply = {}
    reply["fulfillmentText"] = " "
    reply["fulfillmentMessages"] = msgs    

    return reply

def build_Card_Msg(title, subtitle, imageurl, buttons):
    reply = {}
    reply["fulfillmentText"] = " "  
    reply["fulfillmentMessages"] =  [
      {
        "card": {
             "title": title,
             "subtitle": subtitle,
             "imageUri": imageurl,
             "buttons": buttons
        },
        "platform": "SLACK"
      },
      {
        "card": {
             "title": title,
             "subtitle": subtitle,
             "imageUri": imageurl,
             "buttons": buttons
        },
        "platform": "TELEGRAM"
      },
      {
        "card": {
             "title": title,
             "subtitle": subtitle,
             "imageUri": imageurl,
             "buttons": buttons
        }
      }
    ]
    return reply

def build_MultiCard_Msg(businesses):
    cards = []

    for business in businesses:
        contact = ", ".join(business["location"]["display_address"]) + " [" + business["phone"] + "]"
        address = ",".join(business["location"]["display_address"]).replace(",", "%2C").replace(" ", "+")
        card_slack = {
                            "card": {
                            "title": business["name"],
                            "subtitle": contact,
                            "imageUri": business["image_url"],
                            "buttons": [
                                        {
                                            "text": "See Business Details",
                                            "postback": "Get details of " + business['id']
                                        },
                                        {
                                            "text": "See Business Reviews",
                                            "postback": "Get reviews of " + business['id']
                                        },
                                        {
                                            "text": "Get Directions",
                                            #"postback": "https://www.google.com/maps/search/?api=1&query=" + address
                                            "postback": "https://www.yelp.com/map/" + business["alias"]
                                        },
                                        {
                                            "text": "Visit Yelp page",
                                            "postback": business["url"]
                                        }  
                            ]   
                        },
                        "platform": "SLACK"
        }
        card_telegram = {
                            "card": {
                            "title": business["name"],
                            "subtitle": contact,
                            "imageUri": business["image_url"],
                            "buttons": [
                                        {
                                            "text": "See Details",
                                            "postback": "Get details of " + business['id']
                                        },
                                        {
                                            "text": "See Reviews",
                                            "postback": "Get reviews of " + business['id']
                                        },
                                        {
                                            "text": "Get Directions",
                                            #"postback": "https://www.google.com/maps/search/?api=1&query=" + address
                                            "postback": "https://www.yelp.com/map/" + business["alias"]
                                        },
                                        {
                                            "text": "Visit Yelp page",
                                            "postback": business["url"]
                                        }  
                            ]   
                        },
                        "platform": "TELEGRAM"
        }
        card_default = {
                        "card": {
                            "title": business["name"],
                            "subtitle": contact,
                            "imageUri": business["image_url"],
                            "buttons": [
                                        {
                                            "text": "See Business Details",
                                            "postback": "Get details of " + business['id']
                                        },
                                        {
                                            "text": "See Business Reviews",
                                            "postback": "Get reviews of " + business['id']
                                        },
                                        {
                                            "text": "Get Directions",
                                            #"postback": "https://www.google.com/maps/search/?api=1&query=" + address
                                            "postback": "https://www.yelp.com/map/" + business["alias"]
                                        },
                                        {
                                            "text": "Visit Yelp page",
                                            "postback": business["url"]
                                        }
                            ] 
                        }
        }
        cards.append(card_slack)
        cards.append(card_telegram)
        cards.append(card_default)

    reply = {}
    reply["fulfillmentText"] = " "  
    reply["fulfillmentMessages"] = cards

    return reply

def build_MultiCard_Msg2(businesses):
    cards = []

    for business in businesses:  
        cat_list = []
        for cat in business["Categories"].split(","):
            cat_list.append({
                                "text": cat
                            }
            )
                
        card_slack = {
                        "card": {
                            "title": business["Name"],
                            "subtitle": "Rating: {}".format(business["EstRating"]),
                            "imageUri": "",
                            "buttons": [
                                        {
                                            "text": "See Business Details",
                                            "postback": business['businessID']
                                        },
                                        {
                                            "text": "See Business Reviews",
                                            "postback": "Get reviews of " + business['businessID']
                                        },
                                        {
                                            "text": "Get Directions",
                                            "postback": "https://www.google.com/maps/search/?api=1&query=" + "+".join(business["Address"].split(" ")).replace(",", "%2C")
                                        }                    
                            ]
                        },
                        "platform": "SLACK"
        }
        card_telegram = {
                        "card": {
                            "title": business["Name"],
                            "subtitle": "Rating: {}".format(business["EstRating"]),
                            "imageUri": "",
                            "buttons": [
                                        {
                                            "text": "See Details",
                                            "postback": business['businessID']
                                        },
                                        {
                                            "text": "See Reviews",
                                            "postback": "Get reviews of " + business['businessID']
                                        },
                                        {
                                            "text": "Get Directions",
                                            "postback": "https://www.google.com/maps/search/?api=1&query=" + "+".join(business["Address"].split(" ")).replace(",", "%2C")
                                        }                    
                            ]
                        },
                        "platform": "TELEGRAM"
        }
        card_default = {
                        "card": {
                            "title": business["Name"],
                            "subtitle": "Rating: {}".format(business["EstRating"]),
                            "imageUri": "",
                            "buttons": [
                                        {
                                            "text": "See Business Details",
                                            "postback": "search for " + business['businessID']
                                        },
                                        {
                                            "text": "See Business Reviews",
                                            "postback": "Get reviews of " + business['businessID']
                                        },
                                        {
                                            "text": "Get Directions",
                                            "postback": "https://www.google.com/maps/search/?api=1&query=" + "+".join(business["Address"].split(" ")).replace(",", "%2C")
                                        } 
                            ]
                        }
        }
        cards.append(card_slack)
        cards.append(card_telegram)
        cards.append(card_default)

    reply = {}
    reply["fulfillmentText"] = " "  
    reply["fulfillmentMessages"] = cards

    return reply

def generateImgMosaic(head_url, img_urls):
    space_between_row = 10
    new_image_path = 'result.jpg'

    # get sorted list of images
    #head_url = "https://s3-media2.fl.yelpcdn.com/bphoto/CPc91bGzKBe95aM5edjhhQ/o.jpg"
    #img_urls = ['https://s3-media2.fl.yelpcdn.com/bphoto/CPc91bGzKBe95aM5edjhhQ/o.jpg', 
    #        'https://s3-media4.fl.yelpcdn.com/bphoto/FmXn6cYO1Mm03UNO5cbOqw/o.jpg',
    #        'https://s3-media4.fl.yelpcdn.com/bphoto/HZVDyYaghwPl2kVbvHuHjA/o.jpg']

    # concat images
    total_width = 300
    total_height = 200
    new_im = Image.new('RGB', (total_width, total_height))
    y_offset = 0
    x_offset = 0
    max_height = 0

    for url in img_urls:
        image = Image.open(urllib.request.urlopen(url)).resize((100,100))
        new_im.paste(image, box=(x_offset, y_offset))
        width, height = image.size
        x_offset += width
        max_height = max(height, max_height)
    y_offset = y_offset + max_height + space_between_row

    image = Image.open(urllib.request.urlopen(head_url)).resize((300,100))
    new_im.paste(image, box=(0, 100))

    new_im.save(new_image_path) 


def uploadImageToGCP(imgName):
    bucket_name = 'yelperassistant.appspot.com'
    object_name = imgName + ".jpg"
    client = storage.Client.from_service_account_json('YelperAssistant-e4bf0d9b47c3.json')
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob("images/{}.jpg".format(imgName))
    blob.upload_from_filename("result.jpg")

    #returns a public url
    print(blob.public_url)

if __name__ == "__main__":
    app.run()