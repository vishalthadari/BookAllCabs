from __future__ import print_function
from flask import Flask, session, request, redirect, url_for
from OlaClient import OlaCabsClient
from UberClient import Uber_api 
from templates import AttachmentTemplate, LoginButton, ola_cars, fetch_uberCars_templates, rider_details, details_driver, ola_driver_details, cheap_ola, fetch_cheap_uberCars_templates, fetch_cheap_cars, fetch_uberCars_bysort, get_ola_bysort, LoginButtonOla, get_user_information
from store_pickle import store_cred, retrieve_cred
import pickle
import requests
import json
import apiai

ACCESS_TOKEN = "EAABeicIfFkYBAPZAA3qGYcWeP7LNW44nZCxj2Nhlb58rjcBqVevKlMBpbjNInBZAIJC3H73ZAZACluwOCKFEwofhFRgT0tdPyTiR7BRH9qakPYwTNSLqXxUZCZAjEMuMUZB7ZBlg1TsJIJk8J5Mmk2ZCoI3XFCpm6dH4mHaZBfZAjMW9hQZDZD"
APIAI_TOKEN="80e5f7e66b404410878cbf9e55f0a155"
VERIFY_TOKEN = "book_cab_now"

app = Flask(__name__)

g_context = {}
print(g_context)

global req
global context
global g_Uber
g_Uber = Uber_api()

ai = apiai.ApiAI(APIAI_TOKEN)

@app.route('/', methods=['GET'])
def verify():
	
	if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
	
		if not request.args.get("hub.verify_token") == VERIFY_TOKEN:
			return "Verification token mismatch", 403
		return request.args["hub.challenge"], 200
	return 'Hello World (from Flask!)', 200

@app.route('/', methods=['POST'])
def handle_incoming_messages():
	
	if request.method == "POST":
		data = request.json	
		print ("Data Function1 ::\n") 
		print (json.dumps(data, indent=4, sort_keys=True))
		print('data enters here.....')
		global senderId
		senderId = data['entry'][0]['messaging'][0]['sender']['id']
		req = data['entry'][0]['messaging'][0]
		DEFAULT_MAX_STEPS = 5
		global g_context
		
		if "message" in req:
			print ('enter message')
			
			if "text" in req['message']:
				text = req['message']['text']
				print (json.dumps(text, indent=4, sort_keys=True))
				parse(text)
				
				if 'payload' in res['fulfillment']['messages'][0]: 
					message = res['fulfillment']['messages'][0]['payload']['facebook']
				
				else:
					message = {'text':res['fulfillment']['speech']}
				
				print ("\nMessage ::\n")
				print (json.dumps(message, indent=4, sort_keys=True))
				actions[action](senderId,message)
				actionIncomplete = res.get('actionIncomplete', False)
				return "ok"

			elif "attachments" in req['message']:
				print('entering attachment:.......')
				print ("\ng_context ::\n")
				print (json.dumps(g_context, indent=4, sort_keys=True))

				if "done" in g_context:
					del g_context['done']
					return "ok"
				
				elif "fastdone" in g_context:
					del g_context['fastdone']
					print (json.dumps(g_context, indent=4, sort_keys=True))
					return "ok"
				
				if req['message']['attachments'][0]['type'] == 'location':
					print('loaction.......')
					title = req['message']['attachments'][0]['title']
					latitude = req['message']['attachments'][0]['payload']['coordinates']['lat']
					longitude = req['message']['attachments'][0]['payload']['coordinates']['long']
					Attchmessage = "latitude= "+str(latitude)+" , longitude: "+str(longitude)
					print(Attchmessage)
					parse(Attchmessage)
					actions[action](senderId, g_context)
					print ("\n CONTEXT :: \n")
					print("status code 200")
					return "ok"
					
				else:
					return "Different Event"

		elif "postback" in req:
			
			if "payload" in req['postback']:
			
				if req['postback'].get('payload')[:6] == "cancel":
					req_id = req['postback'].get('payload')[7:]
					cancel_ride(req_id=str(req_id), sender_id=senderId)
					return "ok"
			
				else:
					print('for payload......')
					print('entering to postback.......')
					print(str(req['postback'].get('payload')))
					pro_id = str(req['postback'].get('payload'))
					booking_ride(pro_id=pro_id, sender_id=senderId)
					return "ok"
		
		else:
			return "Received Different Event"
		
		return "ok"			

@app.route('/uber/test')
def index():
	
	global g_context
	print('redirect to get auth url')
	uber = g_Uber
	state = request.args.get('state')
	code = request.args.get('code')
	global url
	url = "https://35df5552.ngrok.io/uber/test?state="+str(state)+"&code="+str(code)
	g_context['auth_url'] = url
	print (json.dumps(g_context, indent=4, sort_keys=True))
	cred = "state :  "+ str(state)  +"   ||  code :  " +   str(code)
	IMAGE_URL = "https://lh3.googleusercontent.com/iyt_f1j2d2ildbFLDlS0Qf36NJMeRVZFBetcg-pmrkdQtN9C1wUTaFhloKUcwVVfQeg=w300"
	DISPLAY_TEXT = "..........."
	close_url = "https://www.messenger.com/closeWindow/?image_url="+IMAGE_URL+"&display_text="+DISPLAY_TEXT
	return redirect(close_url)

cab_request = {}
cab_request['process'] = False
cab_request['accept'] = False
cab_request['cancel'] = False

@app.route('/uber/request', methods=['POST'])
def request_handler():
	
	print('Processing route..............')
	
	if request.method == 'POST':
		print(g_context['sender_id'])
		print(request.json.get('meta'))
		print(10*'--')
		sender_id = g_context['sender_id']
		print(request.json.get('meta').get('status'))
		global cab_request
	
		if request.json.get('meta').get('status') == 'processing':
	
			if not cab_request['process']:
				cab_request['process'] = True
				print('get processing')
				sendMessage(sender_id, {"text": "processing your cab..."})
	
			else:
				print('processingg.......')
	
		elif request.json.get('meta').get('status') == 'accepted':
			print('accepted')
	
			if not cab_request['accept']:
				cab_request['accept'] = True
				sendMessage(sender_id, {"text": "Your ride accepted..."})
	
			else:
				print('accepting........')
	
		elif request.json.get('meta').get('status') == 'rider_canceled':
			print('cancelled')
	
			if not cab_request['cancel']:
				cab_request['cancel'] = True
				sendMessage(sender_id, {"text": "cab cancelled..."})
	
			else:
				print('cancellinggg........')
	
		else:
			return "some other"

		return " ", 200
	
	else:
		abort(400)

def booking_ride(pro_id='867867t76gff56',sender_id="12421421421"):
	
	uber = g_Uber
	print("product ID ----", pro_id)
	source_ub = './cab_utils/data/uber'
	cred = retrieve_cred(source_ub, sender_id)
	ub_client = uber.get_AuthCredentials(False, cred)
	print('getting estimate price and fare id......')
	estimate = uber.get_estimate_price(product_id=pro_id)
	fare_id = estimate.get('fare_id')
	sender_id = g_context['sender_id']

	try:
		request_ride = uber.request_ride(prod_id=pro_id, fare_id=fare_id)
		print('trying processing.....')
		print("request ID :  ", request_ride.get('request_id'))
		print('processing..................')
		uber.process_request(request_ride.get('request_id'))
		driver_details = uber.riders_details(req_id=request_ride.get('request_id'))
		cancel_button = details_driver(driver=driver_details.get('driver'),status=driver_details.get('status'), location=driver_details.get('location'),payload="cancel="+str(request_ride.get('request_id')))
		sendMessage(sender_id, cancel_button)

	except:
		print('cancelling current ride.....')
		cancel_current = uber.cancel_current_ride()
		print('processing req.....')
		request_ride = uber.request_ride(prod_id=pro_id, fare_id=fare_id)
		print("request ID :  ", request_ride.get('request_id'))	
		print('processing..................')
		uber.process_request(request_ride.get('request_id'))
		driver_details = uber.riders_details(req_id=request_ride.get('request_id'))
		cancel_button = details_driver(driver=driver_details.get('driver'),status=driver_details.get('status'), location=driver_details.get('location'),payload="cancel="+str(request_ride.get('request_id')))
		sendMessage(sender_id, cancel_button)

def cancel_ride(req_id="", sender_id="12214412421421"):
	
	uber = g_Uber
	source_ub = './cab_utils/data/uber'
	cred = retrieve_cred(source_ub, sender_id)
	ub_client = uber.get_AuthCredentials(False, cred)
	cancel = uber.cancel_ride(req_id=str(req_id))
	return "ride cancelled"

def sendMessage(sender_id, message):

	data = {
	'recipient': {'id': sender_id},
	'message': message
			}
	print ("Send Message ::\n")
	print (json.dumps(message, indent=4, sort_keys=True))
	qs = 'access_token=' + ACCESS_TOKEN
	resp = requests.post('https://graph.facebook.com/v2.6/me/messages?' + qs,
						 json=data)
	print("\nresp.content::\n")
	print (json.dumps(resp.content, indent=4, sort_keys=True))

def loading_action(sender_id, message):
	
	data = {
	"recipient": {"id": sender_id},
	"sender_action":"typing_on"
	}
	print ("Loading Action :: \n")
	qs = 'access_token=' + ACCESS_TOKEN
	resp = requests.post('https://graph.facebook.com/v2.6/me/messages?' + qs,
						 json=data)
	print("\nresp.content::\n")
	print (json.dumps(resp.content, indent=4, sort_keys=True))

def make_quickreplies(reply):
	
	return {
		  'content_type': 'text',
		   'title': reply,
		  'payload': reply,
			}

	print ("Quickreplies\n")

def yes_no(sender_id, reply):
	
	arr = []
	
	for i in range(len(reply)):
		Qr = {
			"content_type" : "text",
			"title": reply[i],
			"payload": reply[i]
		}
		arr.append(Qr)
	return arr

def options_reply(sender_id, reply):

	arr = []

	for i in range(len(reply)):
		Qr = {
			"content_type" : "text",
			"title": reply[i],
			"payload": reply[i]
		}
		arr.append(Qr)
	return arr

def get_coordinates(request):

	print ("Entering get_coordinates............")
	title = request['message']['attachments'][0]['title']
	lat = request['message']['attachments'][0]['payload']['coordinates']['lat']
	lng = request['message']['attachments'][0]['payload']['coordinates']['long']
	return {'title': title, 'lat': lat, 'long': lng}

def get_greet(sender_id, request):

	context = request
	print('entering greeting function.......')
	context['sender_id'] = sender_id

	if "done" and 'uber_in' in context:
		del context['done']

	elif "fastdone" in context:
		del context['fastdone']
		print (json.dumps(context, indent=4, sort_keys=True))

	uber = g_Uber
	print('greet function.........')
	print ("Context :: \n")
	print (json.dumps(context, indent=4, sort_keys=True))
	source_ub = './cab_utils/data/uber'
	credential = retrieve_cred(source_ub, sender_id)
		
	if credential is None:
		sendMessage(sender_id, {'text': 'Welcome :D'})
		
	else:
		user_info = get_user_information(sender_id, ACCESS_TOKEN)
		sendMessage(sender_id, {'text': 'Welcome '+str(user_info.get('first_name'))+'  :D'})
	
	return context

def check_cab_options(sender_id, request):

	context = request['context']['result']['contexts'][0]
	sender_id = senderId
	print('entering check_cab_function.......')
	print('context is : \n')
	print (json.dumps(context, indent=4, sort_keys=True))
	uber = g_Uber
	source_ub = './cab_utils/data/uber'
	cred = retrieve_cred(source=source_ub, fbid=sender_id)
	print ("Cred\n")
	print (cred)
	
	if cred is None:
		log_url = uber.get_AuthUrl()
		login_but = LoginButton(text="Login in to UBER account to access CAB", url=log_url)
		sendMessage(sender_id, login_but.get_message())
		context['uber_in'] = False
	
	else:
		context['uber_in'] = True
		sendMessage(sender_id, {"text": "uber in.."})
		
	context['choose'] = {"cab": cab}
	context['missingOrigin'] = True
	print('context at check_cab_options : .....\n')
	print (json.dumps(context, indent=4, sort_keys=True))
	return context

def get_url(record):
    return 'some-url'

def get_origin(sender_id, request):

	print (json.dumps(request, indent=4, sort_keys=True))
	context = request['context']['result']['contexts']
	sender_id = senderId
	print('entering get_origin.......')
	uber = g_Uber
	source_ub = './cab_utils/data/uber'
	index()
	print('context is : \n')
	print (json.dumps(context, indent=4, sort_keys=True))
	cred = uber.get_AuthCredentials(g_context["auth_url"], False)
	store_cred(source_ub, sender_id, cred)
	origin = get_coordinates(request)
	context['origin'] = origin['title']
	context['origin_res'] = origin
	print('context at get_origin : ....\n')
	print (json.dumps(context, indent=4, sort_keys=True))
	return context

def get_destination(sender_id, request):

	context = request['context']['result']['contexts'][0]
	print('entering get_destination.......')
	print('context is : \n')
	print (json.dumps(context, indent=4, sort_keys=True))
	destination = get_coordinates(request)
	context['destination'] = destination['title']
	context['destination_res'] = destination
	del context['missingOrigin']
	print('context at get_destination : ...\n')
	print (json.dumps(context, indent=4, sort_keys=True))
	return context

def get_cabs(sender_id, request):

	context = request['context']['result']['contexts'][0]
	sender_id = senderId
	print('entering get_cabs.........')
	print('context is : \n')
	print (json.dumps(context, indent=4, sort_keys=True))
	uber = g_Uber
	del context['destination']
	del context['origin']
	print(' products fetched from uber.......')
	loading_action(sender_id)
	attach = fetch_attch(sender_id, context)
	print('Get templates sending to fb chat')
	sendMessage(sender_id, {'text': 'showing cabs'})
	sendMessage(sender_id, attach)
	context['done'] = True
	print('context at get_cabs : ...\n')
	print (json.dumps(context, indent=4, sort_keys=True))
	return context

def fetch_attch(sender_id, context):

	conv = context[0]['parameters']['Latitude'][0]
	st_lng = context[0]['parameters']['Longitude'][0]
	conv1 = context[0]['parameters']['Longitude'][0]
	ed_lng = context[0]['parameters']['Longitude'][0]
	print ("\nEntering fetch_attch..............\n")
	st_lat = ".".join( str(x) for x in conv )
	print (st_lat)
	print (st_lng)
	ed_lat = ".".join( str(x) for x in conv1 )
	print (ed_lat)
	print (ed_lng)
	
	if "choose" in context:
		
		if context['choose']['cab'] == 'uber':
			source_ub = './cab_utils/data/uber'
			attach = fetch_uberCars_templates(star_latitude=st_lat, star_longitude=st_lng, en_latitude=ed_lat, en_longitude=ed_lng, sd_id=sender_id)
		
		else:
			attach = {'text': "no cabs found"}
	else:
		print('choose is not there....')
	
	return attach

def clear_context(sender_id, request):

	context = request['context']['result']['contexts'][0]
	del context['destination_res']
	del context['origin_res']
	del context['choose']
	context['done'] = True
	print("in clear context......\n")
	print (json.dumps(context, indent=4, sort_keys=True))
	return context

def parse(string):
	
	receive = ai.text_request()
	receive.query = string
	response = receive.getresponse()
	dump = json.loads(response.read().decode('utf-8'))
	print (json.dumps(dump, indent=4, sort_keys=True))
	g_context["context"] = dump
	global res
	res = dump['result']
	global action
	action = res.get('action')
	print ("\nAction is ::\n")
	print (json.dumps(action, indent=4, sort_keys=True))
	output = dump['result']['fulfillment']['speech']

actions = {
	'sendMessage': sendMessage,
	'getGreet': get_greet,
	'checkCabOptions': check_cab_options,
	'get_origin': get_origin,
	'getDestination': get_destination,
	'getCabs': get_cabs,
	'get_coordinates' : get_coordinates,
	'clearContext' : clear_context,
	'input.unknown' : sendMessage
}

if __name__ == '__main__':
	app.run(debug=True, port=50023)
