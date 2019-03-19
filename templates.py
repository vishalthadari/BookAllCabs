from UberClient import Uber_api
from uber_rides.session import Session
from uber_rides.client import UberRidesClient
from store_pickle import retrieve_cred
import requests




def html_template(price, pro_id, fr_id):
    action_url = "/book_request_ride?fr_id="+fr_id+"&pr_id="+pro_id
    temp = "<h1>"+str(price)+"</h1>"
    form = "<form action ="+ str(action_url)+' method="post"><input type="submit" value="Request Ride"> </form>'
    return temp+form

## File attachment templates
template = {
    "attachment":{
      "type":"image",
      "payload":{
        "url":"https://petersapparel.com/img/shirt.png"
      }
    }
  }

class AttachmentTemplate:
    def __init__(self, url='', type='file'):
        self.template = template
        self.url = url
        self.type = type
    def set_url(self, url=''):
        self.url = url
    def set_type(self, type=''):
        # image / audio / video / file
        self.type = type
    def get_message(self):
        self.template['attachment']['payload']['url'] = self.url
        self.template['attachment']['type'] = self.type
        return self.template




# Login Button Templates

login = {
    "attachment": {
        "type": "template",
        "payload": {
            "template_type": "button",
            "text": "Login with uber",
            "buttons": [
                {
                    "type": "web_url",
                    "url": "log_url",
                    "title": "login"
                }
            ]
        }
    }
}

def details_driver(driver="",location="",payload="", status=''):
    elements = []
    temp  =  {
                "title": str(driver['name']+"           Rating :  "+str(driver['rating'])),
                "image_url": str(driver['picture_url']),
                "subtitle": "Cab staus is "+str(status)+". You can CALL driver or CANCEL with CANCEL BUTTON"
                ,
                "buttons": [
                    {
                        "type":"phone_number",
                        "title":"Call Driver",
                        "payload": str(driver['phone_number'])

                    },
                    {
                        "title": "Cancel Ride",
                        #"type": "web_url"
                        "type": "postback",
                        #"url": url+"/book_request_ride?pro_id="+str(sort_p[i]['pro_id']),
                        "payload":str(payload)
                    }
                ]
            }
    elements.append(temp)
    attachment = {
    "attachment": {
        "type": "template",
        "payload": {
            "template_type": "generic",
            "elements": elements
            }
        }
    }

    return attachment



def rider_details(driver="",location="",payload="", status=''):
    details = {
    "attachment": {
        "type": "template",
        "payload": {
            "template_type": "button",
            "text": "Book a cab with : "+str(driver)+ "  at pickup location : " + str(location) +" on "+str(status) +"   you can cancel ride with pressing cancel button",
            "buttons": [
                {
                    "type": "postback",
                    "payload": str(payload),
                    "title": "Cancel Ride"
                }
            ]
        }
    }
}
    return details


def ola_driver_details(driver):
    elements = []
    temp  =  {
                "title": str(driver['driver_name']+"           Car model : "+str(driver['car_color'])+" "+str(driver['car_model'])),
                #"image_url": str(driver['picture_url']),
                "subtitle": "Cab staus is "+str(driver['status'])+" "+"Cab no. : "+str(driver['cab_number'])+" "+"OTP no. : "+str(driver['otp']['start_trip']['value']),
                "buttons": [
                    {
                        "type":"phone_number",
                        "title":"Call Driver",
                        "payload": str(driver['driver_number'])

                    },
                    {
                        "title": "Cancel Ride",
                        #"type": "web_url"
                        "type": "postback",
                        #"url": url+"/book_request_ride?pro_id="+str(sort_p[i]['pro_id']),
                        "payload":"ola_cancel="+str(driver['crn'])
                    }
                ]
            }
    elements.append(temp)
    attachment = {
    "attachment": {
        "type": "template",
        "payload": {
            "template_type": "generic",
            "elements": elements
            }
        }
    }

    return attachment




class LoginButton:
    def __init__(self, text="", url=""):
        self.login = login
        self.text = text
        self.url = url
    def get_message(self):
        self.login['attachment']['payload']['text'] = self.text
        self.login['attachment']['payload']['buttons'][0]['url'] = self.url
        return self.login


class LoginButtonOla:
    def __init__(self, text="", url=""):
        self.login = login
        self.text = text
        self.url = url
    def get_message(self):
        self.login['attachment']['payload']['text'] = self.text
        self.login['attachment']['payload']['buttons'][0]['url'] = self.url
        return self.login





def get_products_id_price(start_latitude=37.77, start_longitude=-122.41, end_latitude=37.79, end_longitude=-122.41, sendr_id="454432625654"):
    uber = Uber_api
    source_ub = './cab_utils/data/uber'
    credits = retrieve_cred(source_ub, sendr_id)
    #ub_client = uber.get_AuthCredentials(False, cred)
    #products = uber.get_products()
    #prices = uber.get_estimate_pricess()
    session = Session(oauth2credential=credits)
    client = UberRidesClient(session)
    products = client.get_products(latitude=start_latitude, longitude=start_longitude).json
    prices = client.get_price_estimates(start_latitude=start_latitude, start_longitude=start_longitude, end_latitude=end_latitude, end_longitude=end_longitude).json
    pro = []
    for i in range(len(products['products'])-1):
        store = {}
        store['title'] = products['products'][i]['display_name']
        store['pro_id'] = products['products'][i]['product_id']
        store['price'] = {'cost': prices['prices'][i]['estimate'], 'high_price': prices['prices'][i]['high_estimate']}
        store['time'] = client.get_pickup_time_estimates(start_latitude=start_latitude, start_longitude=start_longitude,product_id=store['pro_id']).json
        store['image_url'] = products['products'][i]['image']
        store['description'] = products['products'][i]['description']
        store['capacity'] = products['products'][i]['capacity']
        pro.append(store)
        
    return pro

def fetch_uberCars_templates(star_latitude=37.77, star_longitude=-122.41, en_latitude=37.79, en_longitude=-122.41, sd_id="4234324324324324"):
    elements = []
    pro = get_products_id_price(start_latitude=star_latitude, start_longitude=star_longitude, end_latitude=en_latitude, end_longitude=en_longitude, sendr_id=sd_id)
    sort_p = sorted(pro, key=lambda k: k['price']['high_price'], reverse=False)
    for i in range(0,len(sort_p)):
        try:
            desc = "capacity : "+str(sort_p[i]['capacity'])+" | Time :  "+str(float(sort_p[i]['time']['times'][0]['estimate']/ 60))+" min"+" | "+str(sort_p[i]['description'])
        except:
            desc = "Not available"

        temp  =  {
                "title": str(sort_p[i]['title'].encode('utf-8')+"        "+str(sort_p[i]['price']['cost'].encode('utf-8'))),
                "image_url": str(sort_p[i]['image_url']),
                "subtitle": desc,
                "default_action": {
                    "type": "web_url",
                    "url": "https://www.uber.com/",
                    "webview_height_ratio": "tall"
                },
                "buttons": [
                    {
                        "title": "BOOK",
                        #"type": "web_url"
                        "type": "postback",
                        #"url": url+"/book_request_ride?pro_id="+str(sort_p[i]['pro_id']),
                        "payload":str(sort_p[i]['pro_id'])
                    }
                ]
            }
        elements.append(temp)


    attachment = {
    "attachment": {
        "type": "template",
        "payload": {
            "template_type": "generic",
            "elements": elements
        }
    }
}


    return attachment






ola_cars = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "buttons": [
                            {
                                "type": "postback",
                                "payload": "ola_book=share",
                                "title": "BOOK"
                            }
                        ],
                        "subtitle": "ETA : -1 minute | distance : -1 kilometre",
                        "default_action": {
                            "url": "https://www.olacabs.com/",
                            "webview_height_ratio": "tall",
                            "type": "web_url"
                        },
                        "image_url": "http://d1foexe15giopy.cloudfront.net/share.png",
                        "title": "Ola Share        Base Fare : N/A"
                    },
                    {
                        "buttons": [
                            {
                                "type": "postback",
                                "payload": "ola_book=micro",
                                "title": "BOOK"
                            }
                        ],
                        "subtitle": "ETA : 3 minute | distance : 0.3 kilometre",
                        "default_action": {
                            "url": "https://www.olacabs.com/",
                            "webview_height_ratio": "tall",
                            "type": "web_url"
                        },
                        "image_url": "http://d1foexe15giopy.cloudfront.net/micro.png",
                        "title": "Ola Micro        Base Fare : Rs. 40"
                    },
                    {
                        "buttons": [
                            {
                                "type": "postback",
                                "payload": "ola_book=mini",
                                "title": "BOOK"
                            }
                        ],
                        "subtitle": "ETA : 2 minute | distance : 0.3 kilometre",
                        "default_action": {
                            "url": "https://www.olacabs.com/",
                            "webview_height_ratio": "tall",
                            "type": "web_url"
                        },
                        "image_url": "http://d1foexe15giopy.cloudfront.net/mini.png",
                        "title": "Ola Mini        Base Fare : Rs.50"
                    },
                    {
                        "buttons": [
                            {
                                "type": "postback",
                                "payload": "ola_book=sedan",
                                "title": "BOOK"
                            }
                        ],
                        "subtitle": "ETA : -1 minute | distance : -1 kilometre",
                        "default_action": {
                            "url": "https://www.olacabs.com/",
                            "webview_height_ratio": "tall",
                            "type": "web_url"
                        },
                        "image_url": "http://d1foexe15giopy.cloudfront.net/prime.png",
                        "title": "Ola Sedan      Base Fare : Rs.50"
                    }
                ]
            }
        }
    }


cheap_ola = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "buttons": [
                            {
                                "type": "postback",
                                "payload": "ola_book=share",
                                "title": "BOOK"
                            }
                        ],
                        "subtitle": "ETA : -1 minute | distance : -1 kilometre",
                        "default_action": {
                            "url": "https://www.olacabs.com/",
                            "webview_height_ratio": "tall",
                            "type": "web_url"
                        },
                        "image_url": "http://d1foexe15giopy.cloudfront.net/share.png",
                        "title": "Ola Share        Base Fare : N/A"
                    },
                    {
                        "buttons": [
                            {
                                "type": "postback",
                                "payload": "ola_book=micro",
                                "title": "BOOK"
                            }
                        ],
                        "subtitle": "ETA : 3 minute | distance : 0.3 kilometre",
                        "default_action": {
                            "url": "https://www.olacabs.com/",
                            "webview_height_ratio": "tall",
                            "type": "web_url"
                        },
                        "image_url": "http://d1foexe15giopy.cloudfront.net/micro.png",
                        "title": "Ola Micro        Base Fare : Rs. 40"
                    }
                ]
            }
        }
    }



def fetch_cheap_uberCars_templates(star_latitude=37.77, star_longitude=-122.41, en_latitude=37.79, en_longitude=-122.41,sender_id="12141414141"):
    elements = []
    pro = get_products_id_price(start_latitude=star_latitude, start_longitude=star_longitude, end_latitude=en_latitude, end_longitude=en_longitude, sendr_id=sender_id)
    sort_p = sorted(pro, key=lambda k: k['price']['high_price'], reverse=False)
    sort_p = sort_p[:2]
    for i in range(0,len(sort_p)):
        try:
            desc = "capacity : "+str(sort_p[i]['capacity'])+" | Time :  "+str(float(sort_p[i]['time']['times'][0]['estimate']/ 60))+" min"+" | "+str(sort_p[i]['description'])
        except:
            desc = "Not available"

        temp  =  {
                "title": str(sort_p[i]['title'].encode('utf-8')+"        "+str(sort_p[i]['price']['cost'].encode('utf-8'))),
                "image_url": str(sort_p[i]['image_url']),
                "subtitle": desc,
                "default_action": {
                    "type": "web_url",
                    "url": "https://www.uber.com/",
                    "webview_height_ratio": "tall"
                },
                "buttons": [
                    {
                        "title": "BOOK",
                        #"type": "web_url"
                        "type": "postback",
                        #"url": url+"/book_request_ride?pro_id="+str(sort_p[i]['pro_id']),
                        "payload":str(sort_p[i]['pro_id'])
                    }
                ]
            }
        elements.append(temp)


    attachment = {
    "attachment": {
        "type": "template",
        "payload": {
            "template_type": "generic",
            "elements": elements
        }
    }
}


    return attachment





def fetch_cheap_cars(star_latitude=37.77, star_longitude=-122.41, en_latitude=37.79, en_longitude=-122.41, snd_id="325325325235"):
    elements = cheap_ola['attachment']['payload']['elements']
    pro = get_products_id_price(start_latitude=star_latitude, start_longitude=star_longitude, end_latitude=en_latitude, end_longitude=en_longitude, sendr_id=snd_id)
    sort_p = sorted(pro, key=lambda k: k['price']['high_price'], reverse=False)
    sort_p = sort_p[:2]
    for i in range(0,len(sort_p)):
        try:
            desc = "capacity : "+str(sort_p[i]['capacity'])+" | Time :  "+str(float(sort_p[i]['time']['times'][0]['estimate']/ 60))+" min"+" | "+str(sort_p[i]['description'])
        except:
            desc = "Not available"

        temp  =  {
                "title": str(sort_p[i]['title'].encode('utf-8')+"        "+str(sort_p[i]['price']['cost'].encode('utf-8'))),
                "image_url": str(sort_p[i]['image_url']),
                "subtitle": desc,
                "default_action": {
                    "type": "web_url",
                    "url": "https://www.uber.com/",
                    "webview_height_ratio": "tall"
                },
                "buttons": [
                    {
                        "title": "BOOK",
                        #"type": "web_url"
                        "type": "postback",
                        #"url": url+"/book_request_ride?pro_id="+str(sort_p[i]['pro_id']),
                        "payload":str(sort_p[i]['pro_id'])
                    }
                ]
            }
        elements.append(temp)


    attachment = {
    "attachment": {
        "type": "template",
        "payload": {
            "template_type": "generic",
            "elements": elements
        }
    }
}


    return attachment



def get_products_bysort(start_latitude=37.77, start_longitude=-122.41, end_latitude=37.79, end_longitude=-122.41, category="pool", sender_id="758758758758"):
    uber = Uber_api
    source_ub = './cab_utils/data/uber'
    cred = retrieve_cred(source=source_ub, fbid=sender_id)
    #ub_client = uber.get_AuthCredentials(False, cred)
    #products = uber.get_products()
    #prices = uber.get_estimate_pricess()
    session = Session(oauth2credential=cred)
    client = UberRidesClient(session)
    products = client.get_products(latitude=start_latitude, longitude=start_longitude).json
    prices = client.get_price_estimates(start_latitude=start_latitude, start_longitude=start_longitude, end_latitude=end_latitude, end_longitude=end_longitude).json
    pro = []
    for i in range(len(products['products'])-1):
        store = {}
        if category in products['products'][i]['display_name'].lower():
            store['title'] = products['products'][i]['display_name']
            store['pro_id'] = products['products'][i]['product_id']
            store['price'] = {'cost': prices['prices'][i]['estimate'], 'high_price': prices['prices'][i]['high_estimate']}
            store['time'] = client.get_pickup_time_estimates(start_latitude=start_latitude, start_longitude=start_longitude,product_id=store['pro_id']).json
            store['image_url'] = products['products'][i]['image']
            store['description'] = products['products'][i]['description']
            store['capacity'] = products['products'][i]['capacity']
            pro.append(store)
        
    return pro

def fetch_uberCars_bysort(star_latitude=37.77, star_longitude=-122.41, en_latitude=37.79, en_longitude=-122.41, category="pool", sender_id="7887876876876"):
    elements = []
    pro = get_products_bysort(start_latitude=star_latitude, start_longitude=star_longitude, end_latitude=en_latitude, end_longitude=en_longitude, category=category, sender_id=sender_id)
    sort_p = sorted(pro, key=lambda k: k['price']['high_price'], reverse=False)
    for i in range(0,len(sort_p)):
        try:
            desc = "capacity : "+str(sort_p[i]['capacity'])+" | Time :  "+str(float(sort_p[i]['time']['times'][0]['estimate']/ 60))+" min"+" | "+str(sort_p[i]['description'])
        except:
            desc = "Not available"

        temp  =  {
                "title": str(sort_p[i]['title'].encode('utf-8')+"        "+str(sort_p[i]['price']['cost'].encode('utf-8'))),
                "image_url": str(sort_p[i]['image_url']),
                "subtitle": desc,
                "default_action": {
                    "type": "web_url",
                    "url": "https://www.uber.com/",
                    "webview_height_ratio": "tall"
                },
                "buttons": [
                    {
                        "title": "BOOK",
                        #"type": "web_url"
                        "type": "postback",
                        #"url": url+"/book_request_ride?pro_id="+str(sort_p[i]['pro_id']),
                        "payload":str(sort_p[i]['pro_id'])
                    }
                ]
            }
        elements.append(temp)


    attachment = {
    "attachment": {
        "type": "template",
        "payload": {
            "template_type": "generic",
            "elements": elements
        }
    }
}


    return attachment


def get_ola_bysort(category="share"):
    if category == "share":
        ola = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "buttons": [
                            {
                                "type": "postback",
                                "payload": "ola_book=share",
                                "title": "BOOK"
                            }
                        ],
                        "subtitle": "ETA : -1 minute | distance : -1 kilometre",
                        "default_action": {
                            "url": "https://www.olacabs.com/",
                            "webview_height_ratio": "tall",
                            "type": "web_url"
                        },
                        "image_url": "http://d1foexe15giopy.cloudfront.net/share.png",
                        "title": "Ola Share        Base Fare : N/A"
                    }
                ]
            }
        }
    }
        return ola
    elif category == "mini":
        ola = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "buttons": [
                            {
                                "type": "postback",
                                "payload": "ola_book=mini",
                                "title": "BOOK"
                            }
                        ],
                        "subtitle": "ETA : 2 minute | distance : 0.3 kilometre",
                        "default_action": {
                            "url": "https://www.olacabs.com/",
                            "webview_height_ratio": "tall",
                            "type": "web_url"
                        },
                        "image_url": "http://d1foexe15giopy.cloudfront.net/mini.png",
                        "title": "Ola Mini        Base Fare : Rs.50"
                    }
                ]
            }
        }
    }
        return ola

    elif category == "micro":
        ola = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "buttons": [
                            {
                                "type": "postback",
                                "payload": "ola_book=micro",
                                "title": "BOOK"
                            }
                        ],
                        "subtitle": "ETA : 3 minute | distance : 0.3 kilometre",
                        "default_action": {
                            "url": "https://www.olacabs.com/",
                            "webview_height_ratio": "tall",
                            "type": "web_url"
                        },
                        "image_url": "http://d1foexe15giopy.cloudfront.net/micro.png",
                        "title": "Ola Micro        Base Fare : Rs. 40"
                    }
                ]
            }
        }
    }
        return ola
    elif category == "sedan":
        ola = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "buttons": [
                            {
                                "type": "postback",
                                "payload": "ola_book=sedan",
                                "title": "BOOK"
                            }
                        ],
                        "subtitle": "ETA : -1 minute | distance : -1 kilometre",
                        "default_action": {
                            "url": "https://www.olacabs.com/",
                            "webview_height_ratio": "tall",
                            "type": "web_url"
                        },
                        "image_url": "http://d1foexe15giopy.cloudfront.net/prime.png",
                        "title": "Ola Sedan      Base Fare : Rs.50"
                    }
                ]
            }
        }
    }
        return ola
    else:
        print("no more cabs available")




def get_user_information(fbid,PAGE_ACCESS_TOKEN):
    GRAPH_URL = ("https://graph.facebook.com/v2.7/{fbid}")
    user_info_url = GRAPH_URL.format(fbid=fbid)
    payload = {}
    payload['fields'] = 'first_name,last_name,gender,profile_pic,\
    locale,timezone,is_payment_enabled,last_ad_referral'
    payload['access_token'] = PAGE_ACCESS_TOKEN
    user_info = requests.get(user_info_url, payload).json()
    return user_info








