import requests

STAGE_URL = "http://sandbox-t.olacabs.com/v1/"


class OlaCabsClient(object):
    def __init__(self, x_app_token):
        self.api_url = STAGE_URL
        self.x_app_token = x_app_token

    def search_ride(self, pickup_lat, pickup_lng, category=None):
        params = {
            "pickup_lat": pickup_lat,
            "pickup_lng": pickup_lng
        }
        if category:
            params['category'] = category

        headers = {
            "X-APP-TOKEN": self.x_app_token
        }
        return self._get("products", headers, params)

    def get_ride_estimate(self, pickup_lat, pickup_lng, drop_lat, drop_lng, category):
        params = {
            "pickup_lat": pickup_lat,
            "pickup_lng": pickup_lng,
            "drop_lat": drop_lat,
            "drop_lng": drop_lng,
            "category": category
        }

        headers = {
            "X-APP-TOKEN": self.x_app_token
        }
        return self._get("products", headers, params)

    def book_ride(self, pickup_lat= "13.007046", pickup_lng = "77.688839", category ="mini", oauthtoken="8ba2b3ee7172425d95677e6ad0ab0dc1", pickup_mode="NOW"):
        params = {
            "pickup_lat": pickup_lat,
            "pickup_lng": pickup_lng,
            "category": category,
            "pickup_mode": pickup_mode
        }

        headers = {
            "X-APP-TOKEN": self.x_app_token,
            "Authorization": "Bearer "+oauthtoken,
            "Content-Type": "application/json"
        }
        return self._post("bookings/create", headers, params)

    def cancel_ride(self, oauthtoken):#, bk_id):
        
        params = {
            "booking_id": "CRN120706398",
            "reason": "Booked another cab"
            
        }

        headers = {
            "X-APP-TOKEN": self.x_app_token,
            "Authorization": oauthtoken
        }
        return self._post("bookings/cancel", headers, params)

    def track_ride(self, oauthtoken):
        headers = {
            "X-APP-TOKEN": self.x_app_token,
            "Authorization": oauthtoken
        }
        return self._get("bookings/track_ride", headers)

    def validate_coupon(self, coupon_code, category, oauthtoken):
        params = {
            "coupon_code": coupon_code,
            "category": category
        }

        headers = {
            "X-APP-TOKEN": self.x_app_token,
            "Authorization": oauthtoken
        }
        return self._get("bookings/cancel", headers, params)

    def _get(self, resource, headers, params=None):
        api_url = self.api_url + resource

        return requests.get(url=api_url,
                            headers=headers,
                            params=params
                            )
    
    def _post(self, resource, headers, params=None):
        
        api_url = self.api_url + resource
        
        return requests.post(url=api_url,
                            headers=headers,
                            params=params)