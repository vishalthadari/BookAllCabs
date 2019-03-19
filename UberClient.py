from yaml import safe_load
from uber_rides.session import Session
from uber_rides.client import UberRidesClient
import time
import os
from uber_rides.auth import AuthorizationCodeGrant
from store_pickle import store_cred, retrieve_cred



CREDENTIALS_FILENAME = os.path.abspath('./config.yaml')



DEFAULT_CONFIG_VALUES = frozenset([
    'INSERT_CLIENT_ID_HERE',
    'INSERT_CLIENT_SECRET_HERE',
    'INSERT_REDIRECT_URL_HERE',
])


def get_auth_url(filename=CREDENTIALS_FILENAME):
    with open(filename, 'r') as config_file:
        config = safe_load(config_file)
        
        client_id = config['client_id']
        client_secret = config['client_secret']
        redirect_url = config['redirect_url']
        
        
        config_values = [client_id, client_secret, redirect_url]

        for value in config_values:
            if value in DEFAULT_CONFIG_VALUES:
                exit('Missing credentials in {}'.format(filename))
        
        credentials = {
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'redirect_url': redirect_url,
                    'scopes': set(config['scopes']),
                }
        
        
        auth_flow = AuthorizationCodeGrant(
        credentials['client_id'],
        credentials['scopes'],
        credentials['client_secret'],
        credentials['redirect_url'])
        
        auth = auth_flow.get_authorization_url()
        
    return auth, auth_flow





class Uber_api(object):
    def __init__(self):
        self.url, self.auth_flow = get_auth_url()
        
        
    def get_AuthUrl(self):
        return self.url
    
    def get_AuthCredentials(self, red_url, cred):
        if red_url:
            session = self.auth_flow.get_session(red_url)
            self.client = UberRidesClient(session, sandbox_mode=False)
            cred = session.oauth2credential
            return cred
        else:
            session = Session(oauth2credential=cred)
            self.client = UberRidesClient(session, sandbox_mode=False)

    
    def user_profile(self):
        
        reponse = self.client.get_user_profile()
        profile = reponse.json
        
        first_name = profile.get('first_name')
        last_name = profile.get('last_name')
        email = profile.get('email')
        
        return first_name, last_name, email
    
    
    def user_history(self):
        
        reponse = self.client.get_user_activity()
        history = reponse.json
        
        return history
    
    def get_products(self, lat=37.77, lng=-122.41):
        
        response = self.client.get_products(lat,lng).json
        #self.product_id = pdct[0].get('product_id')
        
        return response


    def get_estimate_pricess(self, start_latitude=37.77, start_longitude=-122.41, end_latitude=37.79, end_longitude=-122.41):

        res = self.client.get_price_estimates(
                                         start_latitude=start_latitude,
                                         start_longitude=start_longitude,
                                         end_latitude=end_latitude,
                                         end_longitude=end_longitude).json

        return res


    def get_estimate_time(self, start_latitude=37.77, start_longitude=-122.41,product_id='57c0ff4e-1493-4ef9-a4df-6b961525cf92'):


        res = self.client.get_pickup_time_estimates(start_latitude=start_latitude,
                                                    start_longitude=start_longitude,
                                                    product_id=product_id).json

        return res


    
    
    
    def get_estimate_price(self, st_lat=37.77, st_lng=-122.41, dt_lat=37.79, dt_lng=-122.41, seat_count=2, product_id='a1111c8c-c720-46c3-8534-2fcdd730040d'):
        
        estimate = self.client.estimate_ride(
                                    product_id=product_id,
                                    start_latitude=st_lat,
                                    start_longitude=st_lng,
                                    end_latitude=dt_lat,
                                    end_longitude=dt_lng,
                                    seat_count=seat_count)
        est = estimate.json.get('fare')
        #self.fare_id = est['fare_id']
        
        return est
    
    
    
    def request_ride(self, st_lat=37.77, st_lng=-122.41, dt_lat=37.79, dt_lng=-122.41, seat_count=2 ,prod_id='',fare_id=''):
        
    
        response = self.client.request_ride(
                            product_id=prod_id,
                            start_latitude=st_lat,
                            start_longitude=st_lng,
                            end_latitude=dt_lat,
                            end_longitude=dt_lng,
                            seat_count=seat_count,
                            fare_id=fare_id)
        
        req = response.json
        #self.request_id = req.get('request_id')
        
        return req


    def riders_details(self, req_id="221448y7e32ye"):
        res = self.client.get_ride_details(req_id)
        ride = res.json
        
        return ride
    
    def process_request(self, req_id):
        status = 'accepted'
        self.client.update_sandbox_ride(req_id, status)
        #status = ['in_progress','accepted','completed']
#        
#        for i in range(len(status)):
#            self.client.update_sandbox_ride(req_id,status[i])
#            time.sleep(15)

    def cancel_current_ride(self):
        res = self.client.cancel_current_ride()

        return res.json
            
    def cancel_ride(self, req_id):
        res = self.client.cancel_ride(req_id)
        
        return res.json









