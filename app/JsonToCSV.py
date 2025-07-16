import pandas as pd
import os

class GetCSV:
    def __init__(self, path):
        self.path = path

    def __delete_csv(self):
        os.remove(f'{self.path.split('.')[0]}.csv')
    
    def song_json_csv(self):
        data = {
            'Track name': [],
            'Artist name': []
        }
        telegramJson = pd.read_json(self.path)

        for message in telegramJson["messages"]:
            if message.get('media_type') == 'audio_file':
                data['Artist name'].append(message.get('performer', ''))
                data['Track name'].append(message.get('title', ''))
            
            
        df = pd.DataFrame(data)
        df.to_csv(f'{self.path.split('.')[0]}.csv', index=False)

        mySongs = pd.read_csv(f'{self.path.split('.')[0]}.csv')
        self.__delete_csv()

        return mySongs
    
    def export_csv(self, songs:dict):
        df = pd.DataFrame(songs)
        df.to_csv(f'{self.path.split('.')[0]}.csv', index=False)
