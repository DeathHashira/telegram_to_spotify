import pandas as pd

#transferred data
data = {
    'Track name': [],
    'Artist name': []
}

telegramJson = pd.read_json('Jsons/result.json')
for message in telegramJson["messages"]:
    try:
        data['Artist name'].append(message["performer"])
        data['Track name'].append(message["title"])
    except:
        continue

df = pd.DataFrame(data)
df.to_csv('CSVs/test.csv', index=False)