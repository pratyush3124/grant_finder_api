from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
from bson import json_util
from tinydb import TinyDB, Query
from bs4 import BeautifulSoup
import requests
import openai
import os

u1 = "https://blockworks.co"
u2 = "https://superteam.fun"
u3 = "https://www.web3native.co"

def makeFirst():
    resp = requests.get(u1+"/grants", headers = {'User-Agent': 'Popular browser\'s user-agent',})
    html = resp.content

    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find_all('table')[0]
    tbody = table.find_all('tbody')[0]
    grants = tbody.find_all('tr')

    direc1 = []
    keys = ["project", "details", "type", "tags", "deadline", "apply"]

    for grant in grants:
        vals = grant.find_all('td')
        rec = {}
        for i,j in enumerate(vals):
            if i==0:
                rec["img"] = u1+j.find("img")['src']
                rec[keys[i]]=j.text
            elif i==1:
                rec["name"] = j.find("span", class_="text-left text-primary-dark hover:text-primary truncate").text
                rec["link"] = j.find("a")['href']
            elif i==2:
                rec["type"] = [x.text for x in j.find_all("button")]
            elif i==3:
                rec["tags"] = [x.text for x in j.find_all("button")]
            elif i==4:
                pass
            elif i!=5:
                rec[keys[i]]=j.text
            rec["accepting"] = 0
            rec["time"] = 0
        direc1.append(rec)
    return direc1

def makeSecond():
    resp = requests.get(u2+"/instagrants", headers = {'User-Agent': 'Popular browser\'s user-agent'})
    html = resp.content
    soup = BeautifulSoup(html, 'html.parser')
    instagrants = soup.find_all("div", class_="notion-collection-card gallery")
    direc2 = []
    for i in instagrants:
        link = i.find("a")['href']
        name = i.find_all("div")[1].find("span").find_all("span")[1].text
        det = i.find_all("div")[1].find_all("div", class_="notion-collection-card__property")
        accept = det[0].find("span").text
        funding = det[1].find("span", class_="").text
        project = det[2].find("span").text
        tags = det[3].find_all("span")
        tags = [x.text for x in tags]
        link = u2+i.find("a")['href']
        ret = {
            "name":name,
            "accepting":accept,
            "funding":funding,
            "project":project,
            "type":tags,
            "link":link,
            "img":0,
            "time":0,
        }
        direc2.append(ret)
    return direc2

def makeThird():
    def findTags(url):
        resp = requests.get(url, headers = {'User-Agent': 'Popular browser\'s user-agent',})
        soup = BeautifulSoup(resp.content, 'html.parser')
        tags = soup.find_all("div", class_="collection-item-17 w-dyn-item w-col w-col-3")
        link = soup.find("div", class_="div-block-144").find("a")['href']
        return [x.text for x in tags], link
    
    def addGrants(grants, direc):
        for grant in grants:
            funding = grant.find("div", class_="text-block-85").text
            time = grant.find("div", class_="text-block-84").text
            name = grant.find("h5", class_="heading-100").text
            img = grant.find("img")['src']
            project = grant.find("div", class_="text-block-80").text
            a = grant.find("a")['href']
            tags, link = findTags(u3+a)
            print("'", end="")
            ret = {
                "name":name,
                "accepting":0,
                "funding":funding,
                "project":project,
                "tags":tags,
                "time":time,
                "img":img
            }
            direc.append(ret)
        return direc
    
    resp = requests.get(u3+"/grants", headers = {'User-Agent': 'Popular browser\'s user-agent',})
    soup = BeautifulSoup(resp.content, 'html.parser')
    nextb = soup.find("a", class_="w-pagination-next next-6")
    grants = soup.find_all("div", class_="collection-item-19 w-dyn-item w-col w-col-3")
    direc3 = []
    print('-'*96)

    while nextb!=None:
        next_link = u3+"/grants"+nextb['href']
        next_response = requests.get(next_link)
        next_soup = BeautifulSoup(next_response.content, "html.parser")
        nextb = next_soup.find("a", class_="w-pagination-next next-6")
        grants = soup.find_all("div", class_="collection-item-19 w-dyn-item w-col w-col-3")
        direc3 = addGrants(grants, direc3)

    return direc3

db = TinyDB('./grants.json')

app = FastAPI()

@app.get("/findGrants")
async def findGrants():
    return {"grants": db.all()}


@app.get("/scrapeAgain/{password}")
async def scrapeAgain(password):
    if password == "yQBR26tXgAkdHlTTX":
        d1 = makeFirst()
        d2 = makeSecond()
        d3 = makeThird()
        ds = d2+d3+d1
        db.truncate()
        for grant in ds:
            db.insert(grant)
        return "done"
    else:
        return "wrong"

class Item(BaseModel):
    desc: str

with open("/etc/secrets/asdf", "r") as f:
    openai.api_key = f.read()
openai.organization = "org-tBuzVnJ4g5oCThOoLUXr5JJx"

@app.post("/getGpt")
async def getGpt(item:Item):
    prompt = f"""Read the project description given below and tell me in which of the following categories does it fall in, it can fall in more than one category. Answer only in a python list format. The categories are "AI", "Bridges/Interoperability", "CEX", "Communities", "Content", "DeFi", "Derivatives", "DEX", "EVM Compatible","Foundation", "GameFi", "Grants", "Index", "Infrastructure", "Insurance","Inter-operability", "IOT", "Layer 1", "Layer 2", "Lend/Borrow", "Metagovernance", "Music", "NFT", "NFT Marketplace", "Oracles", "Privacy", "Protocal DAO", "Quadratic Funding", "Research", "Social", "Social Causes", "Stablecoin", "Staking", "Yield Farming". The project is '{item.desc}'"""
    resp = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=400,
        temperature=0.1
    )
    text = resp['choices'][0]['text'].strip("\n\n")
    lis = text[1:-1].split(",")
    lis = [x.strip(" ") for x in lis]
    lis = [x.strip('"') for x in lis]
    print(lis)
    return {"categories":lis}
