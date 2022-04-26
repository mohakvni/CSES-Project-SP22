import requests
import json
import webbrowser
import datetime
import csv


client_ID = "0a6420c1d9094c1d81b4b5097d6cd3f1"
client_Secret = "ac4a6d6c55d3445788c79503d23f64c8"
AUTH_URL = 'https://accounts.spotify.com/api/token'

def Get_access() -> tuple:
    scopes = "user-read-playback-state user-read-currently-playing"
    webbrowser.open("https://accounts.spotify.com/authorize?response_type=code&client_id={CLIENT_ID}&scope={scope}&redirect_uri=https://google.com".format(CLIENT_ID = client_ID, scope = scopes))
    redirect = input("enter redirected url: ")
    code = redirect.split("=")[1]
    # POST
    auth_response = requests.post(AUTH_URL,{
        'grant_type': 'authorization_code',
        'client_id': client_ID,
        'client_secret': client_Secret, 
        'code' : code,
        'redirect_uri' : 'https://google.com'
    })
    auth_response_data = auth_response.json()
    access_token = auth_response_data['access_token']
    refresh = auth_response_data['refresh_token']
    return (access_token, refresh)

class Spotify:

    access_token: str
    refresh_token: str
    created: datetime.datetime
    expires: datetime.datetime


    def __init__(self) -> None:
        self.access_token, self.refresh_token = Get_access()
        self.created = datetime.datetime.utcnow()
        self.expires = self.created + datetime.timedelta(minutes=59)
    
    def set_headers(self) -> json :
        if (self.is_expired()):
            self.access_token = self.refresh()
        return {"Content-Type":"application/json",
        'Authorization': 'Bearer {token}'.format(token=self.access_token)
        }
    
    def is_expired(self) -> bool:
        return datetime.datetime.utcnow() > self.expires

    def refresh(self) -> str:
        auth_response = requests.post(AUTH_URL,{
        'grant_type': 'refresh_token',
        'client_id': client_ID,
        'client_secret': client_Secret, 
        'code' : self.refresh_token,
        'redirect_uri' : 'https://google.com'
        })
        auth_response_data = auth_response.json()
        access_token = auth_response_data['access_token']
        return access_token
    def get_songs(self, genres, artists) -> list:
        ultimate = []
        if genres:
            for k in genres:
                for i in range(10, 150, 10):
                    try:
                        params = "q=genre:{genre}&type=track&limit=10&offset={offset}".format(genre = k, offset = i)
                        endpoint_url = "https://api.spotify.com/v1/search?{}".format(params)
                        response  = requests.get(url = endpoint_url, headers=self.set_headers())
                        res = response.json()
                        result = res['tracks']['items']
                        for j in result:
                            if (j['uri'] not in ultimate):
                                ultimate.append(j['uri'])
                    except:
                        continue
        if artists:
            for k in genres:
                for i in range(10, 150, 10):
                    try:
                        params = "q=artist:{artist}&type=track&limit=10&offset={offset}".format(artist = k, offset = i)
                        endpoint_url = "https://api.spotify.com/v1/search?{}".format(params)
                        response  = requests.get(url = endpoint_url, headers=self.set_headers())
                        res = response.json()
                        result = res['tracks']['items']
                        for j in result:
                            if (j['uri'] not in ultimate):
                                ultimate.append(j['uri'])
                    except:
                        continue
        
        return ultimate

    def create_csv(self, genre, artist) -> None:
        newcsv = open("Songs.csv", "w")
        writer = csv.writer(newcsv)
        writer.writerow(["index", "tempo", "instrumentalness", "danceability", "mode", "time_signature", "key"])
        songs_array = self.get_songs(genres=genre, artists=artist)
        song_index = 1
        for i in range(len(songs_array)):
            endpoint_url = "https://api.spotify.com/v1/audio-features/{id}".format(id = songs_array[i][14:])
            res = requests.get(url= endpoint_url, headers=self.set_headers())
            response = res.json()
            keys = [song_index, response["tempo"],response["instrumentalness"],response['danceability'],response['mode'],response['time_signature'],response['key']]
            writer.writerow(keys)
            song_index += 1
    
    def get_UserID(self):
        response = requests.get("https://api.spotify.com/v1/me", headers = self.set_headers())
        content = response.json()
        return content["id"]

    def add_to_queue(self) -> None :
        res = requests.get("https://api.spotify.com/v1/me/player", headers=self.set_headers()).json()
        if(res['device']['is_active']):
            device = res['device']['id']

        

