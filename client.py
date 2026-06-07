import requests

url = "http://18.183.228.89:80/predict"

res = requests.get(url)
#print(res.status_code)

if res.status_code == 200:
    answer = res.json()
    print(answer)
else :
    print(f"Error:{res.status_code}")
    print(res.text)