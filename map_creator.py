import requests
from folium import Map , FeatureGroup , Marker , LayerControl ,Icon
from geopy.geocoders import Nominatim
import json
from pprint import pprint
from flask import Flask , render_template , request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('data.html')

def get_json():
    surl = "https://api.twitter.com/1.1/friends/list.json"
    bearer_token = request.form.get("bearer_token")
    screen_name = request.form.get("screen_name")
    count = request.form.get("friends_count")
    sheaders = {} 
    sheaders["Authorization"] = "Bearer " + bearer_token
    sparams = { 'screen_name': screen_name, 'count': count} 
    response = requests.get(surl, headers=sheaders, params=sparams)
    response_json = response.json()
    with open('data.json', 'w', encoding='utf-8') as file_to_write:
        json.dump(response_json, file_to_write, ensure_ascii=False, indent=4)  
    return response_json



def get_screen_name_and_location(data:dict):
    users = data["users"]
    name_and_location ={}
    for user in users:
        if user["location"] != "":

            name_and_location[user["screen_name"]] = user["location"]
    return  name_and_location

def get_locations_coordinates(name_and_location:dict):
    name_and_coordinates = {}
    geolocator = Nominatim(user_agent='maap') 
    for name in name_and_location:
        
        try:
            location = geolocator.geocode(name_and_location[name]) 
            name_and_coordinates[name] = [location.latitude,location.longitude]
        except AttributeError:
            continue
    return name_and_coordinates


def generate_map(name_and_coordinates:dict):
    mp = Map( zoom_start=15) 
    markers = FeatureGroup() 
    for screen_name in name_and_coordinates:
        markers.add_child(Marker(location=[name_and_coordinates[screen_name][0], name_and_coordinates[screen_name][1]], 
                                    popup=screen_name, 
                                    icon=Icon())) 
    mp.add_child(markers) 
    mp.add_child(LayerControl()) 
 
    return mp._repr_html_()

def main():
    response_json = get_json()
    name_and_location = get_screen_name_and_location(response_json)
    name_and_coordinates = get_locations_coordinates(name_and_location)
    maap = generate_map(name_and_coordinates)
    return maap






@app.route("/register",methods =["POST"])
def register():
    maap = main()

    return maap

app.run(debug=True)
