from __future__ import print_function
from flask import Flask, session, request, redirect, url_for
from OlaClient import OlaCabsClient
from UberClient import Uber_api 
from templates import AttachmentTemplate, LoginButton, ola_cars, fetch_uberCars_templates, rider_details, details_driver, ola_driver_details, cheap_ola, fetch_cheap_uberCars_templates, fetch_cheap_cars, fetch_uberCars_bysort, get_ola_bysort, LoginButtonOla, get_user_information
#from bot_decision import decision
from store_pickle import store_cred, retrieve_cred
#from store_session import add_stored_info, _init_store, get_stored_info
#from ms_support import *
#from wit import Wit
import pickle
import requests
import json
import apiai

ACCESS_TOKEN = "EAAD2rwvxHJ8BAEn8JZAPeZAYWmmGA2PLxdUuGzGmJakKTPPOdoE2lVXVPlUUl3xGtsgpg9zOL81k6JELVt8SD1XrnLLyi17HEBBPes6vXYHoobR1Ab3BjHhbwQnwlUbbCEqgngJZCe5PIc0BRYrNTon3FP7u5VlOmfFA35NFspk1uD8NB6zSwSydJtZB5zIZD"

APIAI_TOKEN="80e5f7e66b404410878cbf9e55f0a155"

#WIT_TOKEN = "NQ32TI2YS2YF4SNBM5FVFU5A2AX5WFIV"

VERIFY_TOKEN = "book_cab_now"


app = Flask(__name__)


g_context = {}
print(g_context)


global g_Uber
g_Uber = Uber_api()


ai = apiai.ApiAI(APIAI_TOKEN)

##########################################################################################################
@app.route('/', methods=['GET'])
def verify():
	# our endpoint echos back the 'hub.challenge' value specified when we setup the webhook
	if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
		if not request.args.get("hub.verify_token") == VERIFY_TOKEN:
			return "Verification token mismatch", 403
		return request.args["hub.challenge"], 200
	return 'Hello World (from Flask!)', 200



@app.route('/', methods=['POST'])
def handle_incoming_messages():
	if request.method == "POST":
		
		data = request.json 

		print (json.dumps(data, indent=4, sort_keys=True))

		print('data enters here.....')
		senderId = data['entry'][0]['messaging'][0]['sender']['id']
		req = data['entry'][0]['messaging'][0]


		print(req)
		DEFAULT_MAX_STEPS = 5
		global g_context
		if "message" in req:
			print ('enter message')
			if "text" in req['message']:
				text = req['message']['text']

				print('text message :.....',text)

				receive = ai.text_request() 
				receive.query = text
				response = receive.getresponse()
				dump = json.loads(response.read().decode('utf-8'))	
				print(dump)
				g_context["context"] = dump	
				res = dump['result']		
				action = res.get('action')
				if 'payload' in res['fulfillment']['messages'][0]: 
					message = res['fulfillment']['messages'][0]['payload']['facebook']
				else:
					message = {'text':res['fulfillment']['speech']}
				print(message)
				print(action)
				actions[action](senderId,message)
				actionIncomplete = res.get('actionIncomplete', False)
				
				#g_context = client.run_actions(session_id=senderId, message=text,context=g_context, max_steps=DEFAULT_MAX_STEPS)
				
				return "ok"
			
			elif "attachments" in req['message']:
				print('entering attachment:.......')
				print(g_context)
				if "done" in g_context:
					del g_context['done']
					return "ok"
				elif "fastdone" in g_context:
					del g_context['fastdone']
					print (g_context)
					return "ok"
				if req['message']['attachments'][0]['type'] == 'location':
					print('loaction.......')
					title = req['message']['attachments'][0]['title']
					lat = req['message']['attachments'][0]['payload']['coordinates']['lat']
					lng = req['message']['attachments'][0]['payload']['coordinates']['long']
					Attchmessage = "lat :  "+str(lat)+"  lng :  "+str(lng)+"  title :  "+title
					print(Attchmessage)
					
					output = dump['result']['fulfillment']['speech']
					print("Reply: " + output)

					#g_context = client.run_actions(session_id=senderId, message=Attchmessage,context=g_context, max_steps=DEFAULT_MAX_STEPS)
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
				elif req['postback'].get('payload')[:8] == "ola_book":
					req_ola = req['postback'].get('payload')[9:]
					print('request cab :', req_ola)
					book_ola(req= str(req_ola), sender_id=senderId)
					return "ok"
				elif req['postback'].get('payload')[:10] == "ola_cancel":
					print('cancelling postback....')
					bk_id = req['postback'].get('payload')[11:]
					cancel_ola(bk_id=bk_id)
					return "ok"
				else:
					print('for payload......')
					print
					print('entering to postback.......')
					print(str(req['postback'].get('payload')))
					pro_id = str(req['postback'].get('payload'))
					booking_ride(pro_id=pro_id, sender_id=senderId)
					return "ok"
		else:
			return "Received Different Event"
		return "ok"



###################################################################################
@app.route('/uber/test')
def index():
	global g_context
	#Make call to Uber service to retrieve products
	print
	print('redirect to get auth url')
	uber = g_Uber
	state = request.args.get('state')
	code = request.args.get('code')
	url = "https://3c2f1c6f.ngrok.io/uber/test?state="+str(state)+"&code="+str(code)
	g_context['auth_url'] = url
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
		print
		print(10*'--')
		sender_id = g_context['sender_id']
		print(request.json.get('meta').get('status'))
		global cab_request
		if request.json.get('meta').get('status') == 'processing':
			if not cab_request['process']:
				cab_request['process'] = True
				print('get processing')
				fb_message(sender_id, {"text": "processing your cab..."})
			else:
				print('processingg.......')
		elif request.json.get('meta').get('status') == 'accepted':
			print('accepted')
			if not cab_request['accept']:
				cab_request['accept'] = True
				#img = AttachmentTemplate(url='http://gph.to/2trhVGR', type='image')
				#fb_message(sender_id, img.get_message())
				fb_message(sender_id, {"text": "Your ride accepted..."})
			else:
				print('accepting........')
		elif request.json.get('meta').get('status') == 'rider_canceled':
			print('cancelled')
			if not cab_request['cancel']:
				cab_request['cancel'] = True
				fb_message(sender_id, {"text": "cab cancelled..."})
			else:
				print('cancellinggg........')
		else:
			return "some other"

		return " ", 200
	else:
		abort(400)




@app.route('/ola/tokens', methods=['GET'])
def tokens():
	return '''  <script type="text/javascript">
				var token = window.location.href.split("access_token=")[1]; 
				window.location = "/token?access_token=" + token;
			</script> '''



@app.route('/token', methods=['GET'])
def app_response_token():
	print(request.args.to_dict())
	creds = request.args.to_dict()
	sender_id = g_context['sender_id']
	source_ol = './cab_utils/data/ola'
	store_cred(source_ol, sender_id, creds)

	IMAGE_URL = "http://www.nearbylocation.in/wp-content/uploads/2016/04/nearby-ola.jpg"
	DISPLAY_TEXT = "..........."
	close_url = "https://www.messenger.com/closeWindow/?image_url="+IMAGE_URL+"&display_text="+DISPLAY_TEXT

	return redirect(close_url)




@app.route('/ola')
def ola():

	#state = request.args.get('state')
	print(request.json)

	return {"succes": "true", "name": "tripdairy"}






#################################################################################################
#@app.route('/book_request_ride', methods=['GET','POST'])
#def book_ride():
#	print("Entering booking routing......")
#	uber = g_Uber
#	#if request.method == 'GET':
##        print(g_context['sender_id'])
##        prod_id = request.args.get('pro_id')
##        cred = retrieve_cred('id')
##        ub_client = uber.get_AuthCredentials(False, cred)
##        price = uber.get_estimate_price(product_id=prod_id)
##        print
##        print("getting price of prod",price)
##        str_price = str(price['display'].encode('ascii','ignore'))
##        fare_id = str(price['fare_id'].encode('ascii','ignore'))
##        templ = html_template(str_price, str(prod_id), fare_id)
##        return templ
#	if request.method == 'GET':
#		prod_id = request.args.get('pro_id')
#		print("product ID ---: ",prod_id)
#		cred = retrieve_cred('id')
#		ub_client = uber.get_AuthCredentials(False, cred)
#		estimate = uber.get_estimate_price(product_id=prod_id)
#		fare_id = estimate.get('fare_id')
#		request_ride = uber.request_ride(prod_id=prod_id, fare_id=fare_id)
#		print(request_ride)
#		print("request id : ",request_ride.get('request_id'))
#		#fb_message(g_context['sender_id'], {'text': request_ride.json.get('status')})
#		print('processing..............')
#		process = uber.process_request(request_ride.get('request_id'))
#		print('cancelllinnnggg......')
#		cancel = uber.cancel_ride(request_ride.get('request_id'))
#		return "Processing Your CAb!!! :D"



###########################################################################################
def book_ola(req="mini", sender_id="89698696889"):
	print("booking ola.....")
	x_app_token = "8d5abd0811ed4a09afa2f89b652edbfd"
	source_ol = './cab_utils/data/ola'
	cred = retrieve_cred(source=source_ol, fbid=sender_id)
	access_tok = cred['access_token']
	print(access_tok)
	ola = OlaCabsClient(x_app_token=x_app_token)
	book = ola.book_ride(category=req, oauthtoken=str(access_tok)).json()
	print(book)
	sender_id = g_context['sender_id']

	if book['status'] == "SUCCESS":

		driver = ola_driver_details(driver=book)
		fb_message(sender_id, driver)
		fb_message(sender_id, {"text": "processing your cab..."})
		fb_message(sender_id, {"text": "Your ride accepted..."})
	elif book['status'] == "FAILURE":

		fb_message(sender_id, {"text": book['message']})



def cancel_ola(bk_id="1231244"):
	sender_id = g_context['sender_id']

	print('cancelling ola....')
	print("booking id : ",bk_id)

	fb_message(sender_id, {"text": "cab cancelled..."})







def booking_ride(pro_id='867867t76gff56',sender_id="12421421421"):
	uber = g_Uber
	print("product ID ----", pro_id)
	source_ub = './cab_utils/data/uber'
	cred = retrieve_cred(source_ub, sender_id)
	ub_client = uber.get_AuthCredentials(False, cred)
	print('getting estimate price and fare id......')
	estimate = uber.get_estimate_price(product_id=pro_id)
	fare_id = estimate.get('fare_id')
	#request_ride = uber.request_ride(prod_id=pro_id, fare_id=fare_id)
	#print("request ID :  ", request_ride.get('request_id'))
	#print('processing..................')
	sender_id = g_context['sender_id']

	try:
		request_ride = uber.request_ride(prod_id=pro_id, fare_id=fare_id)
		print('trying processing.....')
		print("request ID :  ", request_ride.get('request_id'))
		print('processing..................')
		uber.process_request(request_ride.get('request_id'))
		driver_details = uber.riders_details(req_id=request_ride.get('request_id'))
		cancel_button = details_driver(driver=driver_details.get('driver'),status=driver_details.get('status'), location=driver_details.get('location'),payload="cancel="+str(request_ride.get('request_id')))
		fb_message(sender_id, cancel_button)
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
		fb_message(sender_id, cancel_button)
	#print('cancelling............')
	#cancel = uber.cancel_ride(request_ride.get('request_id'))

def cancel_ride(req_id="", sender_id="12214412421421"):
	uber = g_Uber
	source_ub = './cab_utils/data/uber'
	cred = retrieve_cred(source_ub, sender_id)
	ub_client = uber.get_AuthCredentials(False, cred)

	cancel = uber.cancel_ride(req_id=str(req_id))

	return "ride cancelled"




def first_entity_value(entities, entity):
	"""
	Returns first entity value
	"""
	if entity not in entities:
		return None
	val = entities[entity][0]['value']
	if not val:
		return None
	return val['value'] if isinstance(val, dict) else val

def fb_message(sender_id, message):

	data = {
	'recipient': {'id': sender_id},
	'message': message
			}
	print(message)
	qs = 'access_token=' + ACCESS_TOKEN
	resp = requests.post('https://graph.facebook.com/v2.6/me/messages?' + qs,
						 json=data)
	print(resp.content)

def sendMessage(sender_id, message):

	data = {
	'recipient': {'id': sender_id},
	'message': message
			}
	print(message)
	qs = 'access_token=' + ACCESS_TOKEN
	resp = requests.post('https://graph.facebook.com/v2.6/me/messages?' + qs,
						 json=data)
	print(resp.content)



def loading_action(sender_id):
	data = {
	"recipient": {"id": sender_id},
	"sender_action":"typing_on"
	}
	qs = 'access_token=' + ACCESS_TOKEN
	resp = requests.post('https://graph.facebook.com/v2.6/me/messages?' + qs,
						 json=data)
	print(resp.content)



def make_quickreplies(reply):
	return {
		  'content_type': 'text',
		   'title': reply,
		  'payload': reply,
			}


def share_location(reply):
	return {
		"content_type":"location",
		"title": "Send",
			}

def yes_no(reply):
	arr = []
	for i in range(len(reply)):
		Qr = {
			"content_type" : "text",
			"title": reply[i],
			"payload": reply[i]
		}
		arr.append(Qr)

	return arr

def options_reply(reply):
	arr = []
	for i in range(len(reply)):
		Qr = {
			"content_type" : "text",
			"title": reply[i],
			"payload": reply[i]
		}
		arr.append(Qr)

	return arr




def send(request, response):
	message = {}
	fb_id = request['session_id']
	#greet = greeting()
	#text = response['text']
	if 'text' in response:
		message['text'] = response['text']
	if 'quickreplies' in response:
		if response['quickreplies']:
			if response['quickreplies'][0] == "send location":
				message['quick_replies'] = map(share_location, response['quickreplies'])
			elif response['quickreplies'][0] == "Book an Ola" or "Book an Uber":
				message['quick_replies'] = map(make_quickreplies, response["quickreplies"])
			elif response['quickreplies'][0] == "yes" or "no":
				qr = response['quickreplies']
				message['quick_replies'] = yes_no(qr)
			elif response['quickreplies'][0] == "ola" or "uber":
				qr = response['quickreplies']
				message['quick_replies'] = options_reply(qr)
	fb_message(fb_id, message)



def get_coordinates(entities):
	title = first_entity_value(entities, 'title')
	lat = first_entity_value(entities, 'lat')
	lng = first_entity_value(entities, 'lng')

	return {'title': title, 'lat': lat, 'long': lng}



#######################################################################################
def get_greet(request):
	entities = request['entities']
	sender_id = request['session_id']
	intent = first_entity_value(entities, "intent")
	context = request['context']

	print
	print('entering greeting function.......')
	print('intent is ~ ~ ', intent)
	print('context is', context)
	print
	context['sender_id'] = sender_id

	if "done" and 'uber_in' in context:
		del context['done']
	elif "fastdone" in context:
		del context['fastdone']
		print (context)



	uber = g_Uber
	if "greet" in intent:
		print('greet function.........')
		print(context)
		#img = AttachmentTemplate(url='https://media.giphy.com/media/tFkMQTuv2MacM/giphy.gif', type='image')
		#fb_message(sender_id, img.get_message())
		source_ub = './cab_utils/data/uber'
		credential = retrieve_cred(source_ub, sender_id)
		if credential is None:
			fb_message(sender_id, {'text': 'Welcome :D'})
			#log_url = uber.get_AuthUrl()
			#login_but = LoginButton(text="Login in to uber account to access CAB", url=log_url)
			#fb_message(sender_id, login_but.get_message())
		else:
			user_info = get_user_information(sender_id, ACCESS_TOKEN)
			#log_url = uber.get_AuthUrl()
			#login_but = LoginButton(text="Login in to uber account to access CAB", url=log_url)
			fb_message(sender_id, {'text': 'Welcome '+str(user_info.get('first_name'))+'  :D'})
	return context


#def store_options(request):
#	entities = request['entities']
#	context = request['context']#

#	intent = first_entity_value(entities, "intent")
#	try:
#		cab = first_entity_value(entities, "cab")
#		car_type = first_entity_value(entities, "type")
#	except:
#		cab = first_entity_value(entities, "cab")#

#	print
#	print('entering store_options........')
#	print('intent is ~~ ',intent)
#	print('context is : ', context)
#	print#

#	if "choice_type" in intent:#

#		if "rebook" in context:
#			del context['rebook']#
#

#		if  car_type:
#			context['choose'] = {"cab": cab, "type": car_type}
#		else:
#			context['choose'] = {"cab": cab}#

#		return context





def check_cab_options(request):
	entities = request['entities']
	context = request['context']
	sender_id = request['session_id']
	intent = first_entity_value(entities, "intent")
	cab = first_entity_value(entities, "cab")

	print
	print('entering check_cab_function.......')
	print('intent is ~~ ',None)
	print('context is : ', context)
	print
	uber = g_Uber
	if cab == 'uber':
		source_ub = './cab_utils/data/uber'
		cred = retrieve_cred(source=source_ub, fbid=sender_id)
		print (cred)
		if cred is None:
			log_url = uber.get_AuthUrl()
			login_but = LoginButton(text="Login in to UBER account to access CAB", url=log_url)
			fb_message(sender_id, login_but.get_message())
			context['uber_in'] = False
		else:
			context['uber_in'] = True
			fb_message(sender_id, {"text": "uber in.."})
		#print ("Error in...")
		#log_url = uber.get_AuthUrl()
		#login_but = LoginButton(text="Login in to UBER account to access CAB", url=log_url)
		#fb_message(sender_id, login_but.get_message())
	elif cab == 'ola':
		source_ol = './cab_utils/data/ola'
		cred = retrieve_cred(source=source_ol, fbid=sender_id)
		if cred is None:
			ola_url = "https://sandbox-t1.olacabs.com/oauth2/authorize?response_type=token&client_id=MmRjZGUwNzMtNGRkNi00YjBkLTlkZTUtM2Y5ZDRhMjljMzEy&redirect_uri=https://3c2f1c6f.ngrok.io/ola/tokens&scope=profile%20booking&state=state123"
			login_but = LoginButton(text="Login in to OLA account to access CAB", url=ola_url)
			fb_message(sender_id, login_but.get_message())
		else:
			fb_message(sender_id, {"text": "Ola in.."})

	if "cab_book" in intent:
		context['choose'] = {"cab": cab}

		context['missingOrigin'] = True
		print('context at check_cab_options : .....', context)
		return context



def get_origin(request):

	entities = request['entities']
	context = request['context']
	sender_id = request['session_id']
	intent = first_entity_value(entities, 'intent')

	print
	print('entering get_origin.......')
	print('intent is ~~ ', intent)
	print('context is : ', context)
	print
	#uber = g_Uber
#	if context['choose']['cab'] == 'uber':
#		source_ub = './cab_utils/data/uber'
#		cred = uber.get_AuthCredentials(context['auth_url'], False)
#		store_cred(source_ub, sender_id, cred)
#	elif context['choose']['cab'] == 'ola':
#		source_ol = './data/ola'

	uber = g_Uber
	if "coord" in intent:
		if context['choose']['cab'] == 'uber':
			if context['uber_in'] is True:
				pass
			else:
				source_ub = './cab_utils/data/uber'
				cred = uber.get_AuthCredentials(context['auth_url'], False)
				store_cred(source_ub, sender_id, cred)
		elif context['choose']['cab'] == 'ola':
			source_ol = './data/ola'
		origin = get_coordinates(entities)
		context['origin'] = origin['title']
		context['origin_res'] = origin
		print('context at get_origin : ....', context)
		return context


def get_destination(request):
	entities = request['entities']
	context = request['context']

	intent = first_entity_value(entities, "intent")

	print
	print('entering get_destination.......')
	print('intent is  ~~ ', intent)
	print
	print('context is : ', context)
	print

	if "coord" in intent:
		destination = get_coordinates(entities)
		context['destination'] = destination['title']
		context['destination_res'] = destination
		del context['missingOrigin']
		print('context at get_destination : ...', context)
		return context



def get_cabs(request):
	context = request['context']
	sender_id = request['session_id']
	print
	print('entering get_cabs.........')
	print('context is : ', context)
	print
	uber = g_Uber
	del context['destination']
	del context['origin']
	#cred = retrieve_cred('id')
	#ub_client = uber.get_AuthCredentials(False, cred)
	#products = uber.get_products()

	print(' products fetched from uber.......')
	loading_action(sender_id)
	#attach = fetch_uberCars_templates()
	attach = fetch_attch(context, sender_id)
	print('Get templates sending to fb chat')
	fb_message(sender_id, {'text': 'showing cabs'})
	fb_message(sender_id, attach)
	context['done'] = True
	print('context at get_cabs : ...', context)
	return context

def fetch_attch(context, sender_id):
	st_lat = context['origin_res']['lat']
	st_lng = context['origin_res']['long']
	ed_lat = context['destination_res']['lat']
	ed_lng = context['destination_res']['long']
	print(st_lat)
	if "choose" in context:
		if context['choose']['cab'] == 'uber':
			source_ub = './cab_utils/data/uber'
			#cred = retrieve_cred(source_ub, sender_id)
			attach = fetch_uberCars_templates(star_latitude=st_lat, star_longitude=st_lng, en_latitude=ed_lat, en_longitude=ed_lng, sd_id=sender_id)
		elif context['choose']['cab'] == 'ola':
			attach = ola_cars
		else:
			attach = {'text': "no cabs found"}
	else:
		print('choose is not there....')

	return attach


def clear_context(request):
	context = request['context']

	del context['destination_res']
	del context['origin_res']
	del context['choose']

	context['done'] = True
	print("in clear context......",context)

	return context

#def re_booking(request):#

#	context = request['context']#

#	print
#	print('entering re_booking.........')
#	print('context is : ', context)
#	print#

#	context = {}
#	context['rebook'] = True#

#	return context

################ fast book ###########################3

def fast_check_cab_options(request):
	context = request['context']
	entities = request['entities']
	sender_id = request['session_id']
	intent = first_entity_value(entities, "intent")
	context['sender_id'] = sender_id

	if "done" in context:
		del context['done']
	elif "fastdone" in context:
		del context['fastdone']
		print (context)

	#print(entities['cab_type'][0]['value'])
	print(entities)


	if "type" in entities:
		print("type got")
		t_ype = first_entity_value(entities, "type")
		print("price type : ",t_ype)
		cab = first_entity_value(entities, "cab")
		print(cab)
	elif "cab_type" in entities:
		print("cab type got")
		cab_ty = first_entity_value(entities, "cab_type")
		print("cab  type : ",cab_ty)
		cab = first_entity_value(entities, "cab")
		print(cab)
	else:
		print("nothing")


	if "fast_book" in intent:
		context['fastMissingOrigin'] = True
		try:
			if t_ype:
				context['fast_choose'] = {"cab": cab, "type": t_ype}
		except:
			context['fast_choose'] = {"cab": cab, "cab_type": cab_ty}

		print
		print('entering fast_check_cab_options.........')
		print('context is : ', context)
		print


		return context


def fast_get_origin(request):
	entities = request['entities']
	context = request['context']

	intent = first_entity_value(entities, 'intent')


	if "coord" in intent:
		del context['fastMissingOrigin']

		origin = get_coordinates(entities)
		context['fastorigin'] = origin['title']
		context['fast_or_res'] = origin

		print
		print('entering fast_get_origin.........')
		print('context is', context)
		print

		return context



def fast_get_destination(request):
	entities = request['entities']
	context = request['context']

	intent = first_entity_value(entities, 'intent')


	if "coord" in intent:

		destination = get_coordinates(entities)
		context['fastdestination'] = destination['title']
		context['fast_des_res'] = destination

		print
		print('entering fast_get_destination......')
		print('context is', context)
		print


		return context



def fast_get_cabs(request):
	context = request['context']
	sender_id = request['session_id']

	del context['fastorigin']
	del context['fastdestination']

	fb_message(sender_id, {'text': 'showing cabs'})
	fast_choose = context['fast_choose']
	if "cab" and "type" in fast_choose:
		print (fast_choose)
		if fast_choose['type'] == "cheap" and fast_choose['cab'] == "ola":
			fb_message(sender_id, cheap_ola)
		elif fast_choose['type'] == "cheap" and fast_choose['cab'] == "uber":
			cheap_uber = fetch_cheap_uberCars_templates(sender_id=sender_id)
			fb_message(sender_id, cheap_uber)
		elif fast_choose['type'] == "cheap" and fast_choose['cab'] == "cab":
			cheap_cab = fetch_cheap_cars(snd_id=sender_id)
			fb_message(sender_id, cheap_cab)
		else:
			fb(sender_id, {'text': "different type..."})
	elif "cab" and "cab_type" in fast_choose:
		print(fast_choose)
		if fast_choose['cab'] == "uber":
			print("uber cab...")
			catg = fast_choose['cab_type'].lower()
			ppro = fetch_uberCars_bysort(category=catg,sender_id=sender_id)
			fb_message(sender_id, ppro)
		elif fast_choose['cab'] == "ola":
			print("ola cab....")
			cat = fast_choose['cab_type'].lower()
			ola_sort = get_ola_bysort(category=cat)
			fb_message(sender_id, ola_sort)
		elif fast_choose['cab'] == "cab":
			print("cab ....")
		else:
			print('other cab')



	print
	print('entering fast_get_cabs......')
	print('context is', context)
	print

	return context





def fast_clear_context(request):
	context = request['context']

	del context['fast_or_res']
	del context['fast_des_res']
	del context['fast_choose']

	context['fastdone'] = True


	print
	print('entering fast_clear_context.......')
	print('context is', context)
	print

	return context






##############################################################################
# Setup Actions


actions = {
	'sendMessage': sendMessage,
	'getGreet': get_greet,
	#'storeOptions': store_options,
	'checkCabOptions': check_cab_options,
	'getOrigin': get_origin,
	'getDestination': get_destination,
	'getCabs': get_cabs,
	'clearContext' : clear_context,
	#'reBooking': re_booking,
	'fastcheckCabOptions' : fast_check_cab_options,
	'FastgetOrigin' : fast_get_origin,
	'FastgetDestination' : fast_get_destination,
	'FastgetCabs' : fast_get_cabs,
	'FastclearContext' : fast_clear_context,
	'input.unknown' : sendMessage
}




#client = Wit(access_token=WIT_TOKEN, actions=actions)

if __name__ == '__main__':
	app.run(debug=True,port=50023)






#data enters here.....
#{'recipient': {'id': '1419049794811351'}, 'delivery': {'watermark': 1505120045578, 'mids': ['mid.$cAAVQaFYoUW5koWqSClecCVJR9KXO'], 'seq': 0}, 'sender': {'id': '1565766940140355'}, 'timestamp': 1505120045943}
#127.0.0.1 - - [11/Sep/2017 14:24:06] "POST / HTTP/1.1" 200 -
#data enters here.....
#{'message': {'text': 'Hi', 'is_echo': True, 'seq': 91, 'mid': 'mid.$cAAVQaFYoUW5koVkI0VecBO8lvyU2'}, 'recipient': {'id': '1565766940140355'}, 'sender': {'id': '1419049794811351'}, 'timestamp': 1505118896337}
#enter message
#text message :..... Hi






