import requests
import json
import webbrowser
import datetime
import csv
import os
from ClusteringSongs import helper_songs, similar_songs
import threading
import pandas as pd
import time

client_ID = '0a6420c1d9094c1d81b4b5097d6cd3f1' #add your own
client_Secret = 'ac4a6d6c55d3445788c79503d23f64c8' #add your own
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
    num_csvs = 0


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
    def get_songs(self, genres, artists, start=0, end=150) -> list:
        ultimate = []
        if len(genres)!=0:
            for k in genres:
                interval = min(int(end - start), 10)
                for i in range(start, end, interval):
                    try:
                        params = "q=genre:{genre}&type=track&limit={inter}&offset={offset}".format(genre = k, inter=interval, offset = i)
                        endpoint_url = "https://api.spotify.com/v1/search?{}".format(params)
                        response  = requests.get(url = endpoint_url, headers=self.set_headers())
                        res = response.json()
                        result = res['tracks']['items']
                        for j in result:
                            if (j['uri'] not in ultimate):
                                ultimate.append(j['uri'])
                    except:
                        continue
        if len(artists)!=0:
            for k in artists:
                for i in range(0, end, 10):
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

    def create_csv(self, genre, artist, start=0, end=150) -> None:
        newcsv = open("temp_data/Songs{}.csv".format(Spotify.num_csvs), "w")
        Spotify.num_csvs += 1
        writer = csv.writer(newcsv)
        writer.writerow(["index","Song_ID", "name", "artist","tempo", "instrumentalness", "danceability", "mode", "time_signature", "key"])
        songs_array = self.get_songs(genres=genre, artists=artist, start=start, end=end)
        song_index = 1
        for i in range(len(songs_array)):
            try:
                id_song = songs_array[i][14:]
                endpoint_url = f"https://api.spotify.com/v1/audio-features/{id_song}"
                res = requests.get(url= endpoint_url, headers=self.set_headers())
                response = res.json()
                keys = [song_index, id_song, self.name(id_song), self.artist(id_song), response["tempo"],response["instrumentalness"],response['danceability'],response['mode'],response['time_signature'],response['key']]
                writer.writerow(keys)
                song_index += 1
            except:
                continue

    def add_to_queue(self,songs):
        device_id = self.get_device_id
        for song in songs:
            try:
                if (device_id != None):
                    url = "https://api.spotify.com/v1/me/player/queue?uri=spotify%3Atrack%3A{s}&device_id={d}".format(s = song, d = device_id)
                else:
                    url = "https://api.spotify.com/v1/me/player/queue?uri=spotify%3Atrack%3A{s}".format(s = song)
                reponse = requests.post(url,headers=self.set_headers())
                queue = reponse.json()
            except:
                continue


    # Helper Methods, do not touch
    def name(self,id) -> str:
        res = requests.get(f"https://api.spotify.com/v1/tracks/{id}", headers=self.set_headers()).json()
        return res["name"]
    
    def artist(self,id) -> str:
        res = requests.get(f"https://api.spotify.com/v1/tracks/{id}", headers=self.set_headers()).json()
        artist_name=""
        for artist in res["artists"]:
            artist_name += artist["name"] + " "
        return artist_name

    def get_current_song(self):
        response = requests.get("https://api.spotify.com/v1/me/player/curretnly-playing", headers = self.set_headers()).json()
        return response["data"]["externalUrl"][31:]

    def current_song_info(self, song_id):
        response = requests.get("https://api.spotify.com/v1/audio-features/{id}".format(id = song_id), headers = self.set_headers()).json()
        return response
    
    def get_device_id(self) -> None :
        res = requests.get("https://api.spotify.com/v1/me/player", headers=self.set_headers()).json()
        if(res['device']['is_active']):
            device = res['device']['id']
            return device
        else:
            return None
    
    def get_UserID(self):
        response = requests.get("https://api.spotify.com/v1/me", headers = self.set_headers())
        content = response.json()
        return content["id"]

        

def helper(interval, num_songs):
    song = Spotify()
    genre = input("Enter genre: ").lower()
    total_num_songs = 0
    for i in range(0, num_songs, interval):
        j = min(num_songs, i+interval)
        song.create_csv([genre], [], i, j)
        ind = Spotify.num_csvs - 1
        csv = "temp_data/Songs{}.csv".format(ind)
        try:
            songs = pd.read_csv(csv)
            shape = songs.shape
            result = pd.DataFrame(similar_songs(songs, min(shape[0], 1)))
            if ind > 0:
                result.to_csv("Queue.csv", mode = "a", index = False, header = False)
            else:
                result.to_csv("Queue.csv", index = False)
            total_num_songs += result.shape[0]
        except:
             print("Empty")
        if total_num_songs >= num_songs // interval:
            temp_random = pd.read_csv("Queue.csv")
            temp_random = temp_random[:num_songs//interval].to_csv("Queue.csv", index = False)
            break
        os.remove(csv)
    result
    Spotify.num_csvs = 0
    print(str(pd.read_csv("Queue.csv").shape[0]) + " songs added to queue")
        
if __name__ == "__main__":
    # TODO: MULTI-THREADING
    
    # # creating thread
    # t1 = threading.Thread(target=helper, args=(10, 100))
    # t2 = threading.Thread(target=helper_songs, args=())
    
    # # # starting thread 1
    # t1.start()
    # # # starting thread 2
    # t2.start()
    
    # # # wait until thread 1 is completely executed
    # t1.join()
    # # # wait until thread 2 is completely executed
    # t2.join()
    
    helper(10, 100)
    # helper_songs()
  
    # both threads completely executed
    # print("Done!")



