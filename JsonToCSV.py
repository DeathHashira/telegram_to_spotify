import pandas as pd

def song_json_csv(path):
    data = {
        'Track name': [],
        'Artist name': []
    }
    telegramJson = pd.read_json(path)

    for message in telegramJson["messages"]:
        if message.get('media_type') == 'audio_file':
            data['Artist name'].append(message.get('performer', ''))
            data['Track name'].append(message.get('title', ''))
        
        
    df = pd.DataFrame(data)
    df.to_csv('test.csv', index=False)

