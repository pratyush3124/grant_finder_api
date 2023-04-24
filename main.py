from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

app = FastAPI()

def makeDirectory():
    url = "https://blockworks.co/grants"
    resp = requests.get(url,     headers = {
            'User-Agent': 'Popular browser\'s user-agent',
        })
    html = resp.content

    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find_all('table')[0]
    tbody = table.find_all('tbody')[0]
    grants = tbody.find_all('tr')

    directory = []
    keys = ["project", "details", "type", "category", "deadline", "apply"]

    for grant in grants:
        vals = grant.find_all('td')
        rec = {}
        for i,j in enumerate(vals):
            if i==0:
                rec["img"] = j.find("img")['src']
            if i!=5:
                rec[keys[i]]=j.text
            # else:
                # a = j.find_all("a")[0]
                # print(i,rec)
                # rec[keys[i]]=a['href']
        directory.append(rec)
    
    return directory

def searchCateg(direc, categ):
    trueList = []
    for i in direc:
        if categ in i["category"]:
            trueList.append(i)
    return trueList

@app.post("/findGrants")
async def findGrants(body: dict):
    # Do something with the payload
    direc = makeDirectory()
    categ = body['category']
    lis = searchCateg(direc, categ)
    print(lis)

    return {"grants": lis}
