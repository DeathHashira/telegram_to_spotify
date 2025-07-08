from api import UserAccessToken, PlayList
from JsonToCSV import song_json_csv
import pandas as pd
import os, time, requests

path = input("please enter the path of json file: ")
if not os.path.exists(f'{path.split('.')[0]}.csv'):
    song_json_csv(path)

MyAccessToken = UserAccessToken()
if not MyAccessToken.access_token:
        MyAccessToken.get_access_token()
MyPlayList = PlayList(plname='Alireza and Zahra', access_token=MyAccessToken.access_token, 
                        ispublic='false', iscollabrative='false')

mySongs = pd.read_csv(f'{path.split('.')[0]}.csv')

all_uris = {}
numsLists = int(len(mySongs) / 100) + ((len(mySongs) % 100) != 0)
wasted_songs = []
for i in range(numsLists):
    all_uris[f'uris{i+1}'] = []

counter = 1
for row in range(len(mySongs)):
    try:
        songURI = MyPlayList.find_uri(song_name=mySongs['Track name'][row],
                                    artist_name=mySongs['Artist name'][row])
        
        if songURI:
            all_uris[f'uris{counter}'].append(songURI)
        else:
            wasted_songs.append(f'{mySongs['Track name'][row]} - {mySongs['Artist name'][row]}')

        if len(all_uris[f'uris{counter}']) == 100:
            counter += 1
    except requests.exceptions.SSLError:
        wasted_songs.append(f'{mySongs['Track name'][row]} - {mySongs['Artist name'][row]}')
        continue
    
    time.sleep(0.2)

for key in all_uris:
    print(len(all_uris[key]))
    MyPlayList.add_songs(uris=all_uris[key])

print(len(wasted_songs))

