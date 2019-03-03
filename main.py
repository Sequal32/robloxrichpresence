from concurrent.futures import ThreadPoolExecutor
from roblox import ROBLOXClient
from pprint import pprint
from pypresence import Client
import asyncio
import browser_cookie3 as bc
import time
import random
import re
import uuid

#Init everything
partyId = None
maxTrials = 2

# RPC.send({'cmd':'SUBSCRIBE', 'evt':'ACTIVITY_JOIN', 'nonce':str(uuid.uuid4())})
# RPC.send({'cmd':'SUBSCRIBE', 'evt':'ACTIVITY_JOIN_REQUEST', 'nonce':str(uuid.uuid4())})
client = ROBLOXClient(cookie=bc.chrome(domain_name=".roblox.com"))

loop = asyncio.get_event_loop()
_executor = ThreadPoolExecutor(1)

RPC = Client('541669343805833216')
RPC.start()

def JoinRequest(data):
    global partyId
    contents = data['secret']
    placeId = re.search("(\d+)i", contents).group(1)
    serverId = re.search("i(.+)", contents).group(1)

    client.JoinGame(gameId = placeId, serverId=serverId)

    for i in range(maxTrials):
        print("CHECK")
        if client.IsRobloxRunning():
            currentGame = client.GetCurrentGameInfo()
            RPC.set_activity(state=currentGame['lastLocation'], party_id=str(currentGame['placeId']), party_size=[1,20], join=str(currentGame['placeId']) + "i" + str(currentGame['gameId']))
        time.sleep(3)
    partyId = placeId

def ConsentJoin(data):
    userId = data['user']['id']
    RPC.send_activity_join_invite(userId)

RPC.register_event('ACTIVITY_JOIN', JoinRequest)
RPC.register_event('ACTIVITY_JOIN_REQUEST', ConsentJoin)
RPC.handshake()

while True:
    print("Finding game")
    currentGame = client.GetCurrentGameInfo()
    if not currentGame or currentGame['userPresences'][0]['userPresenceType'] != 2:
        RPC.clear_activity()
        partyId = None
        time.sleep(20)
        continue

    currentGame = currentGame['userPresences'][0]
    partyId = random.randint(0, 100000) if (currentGame['placeId'] == None and not partyId) else currentGame['placeId']
    RPC.set_activity(state=currentGame['lastLocation'], party_id=str(currentGame['placeId']), party_size=[1,20], join=str(currentGame['placeId']) + "i" + str(currentGame['gameId']))

    time.sleep(10)