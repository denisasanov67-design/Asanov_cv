import requests
from datetime  import datetime, timedelta

url_template= "https://simurg.space/den_file?data=obs&date={date}"
current = datetime.now()
while True:
    current = current - timedelta(days=1)
    date = current.strftime("%Y-%m-$d")
    print(f"datetime {current} and {date}")
    url = url_template.format(date="2026-02-24")
    response = requests.get(url = url, stream= True) gti
    print(f"From url {url} got {response}")
    if response.status_code == 200:
        break
