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
maxTrials = 7

# RPC.send({'cmd':'SUBSCRIBE', 'evt':'ACTIVITY_JOIN', 'nonce':str(uuid.uuid4())})
# RPC.send({'cmd':'SUBSCRIBE', 'evt':'ACTIVITY_JOIN_REQUEST', 'nonce':str(uuid.uuid4())})
client = ROBLOXClient(cookie=bc.chrome(domain_name=".roblox.com"))

loop = asyncio.get_event_loop()
_executor = ThreadPoolExecutor(1)

RPC = Client('541669343805833216', pipe=0)
RPC.start()

def JoinRequest(data):
    global partyId
    contents = data['secret']
    placeId = re.search("(\d+)i", contents).group(1)
    serverId = re.search("i(.+)", contents).group(1)
    print("Joining %s in Server %s" % (placeId, serverId))
    client.JoinGame(gameId = placeId, serverId=serverId)

    # for i in range(maxTrials):
    #     print("CHECK")
    #     if client.IsRobloxRunning():
    #         currentGame = client.GetCurrentGameInfo()
    #         RPC.set_activity(state=currentGame['lastLocation'], party_id=str(currentGame['placeId']), party_size=[1,20], join=str(currentGame['placeId']) + "i" + str(currentGame['gameId']))
    #         break
    #     time.sleep(3)
    partyId = placeId
    return

def ConsentJoin(data):
    userId = data['user']['id']
    RPC.send_activity_join_invite(userId)

RPC.register_event('ACTIVITY_JOIN', JoinRequest)
RPC.register_event('ACTIVITY_JOIN_REQUEST', ConsentJoin)

async def ActivityLoop():
    while True:
        currentGame = client.GetCurrentGameInfo()
        pprint(currentGame)
        if not currentGame or currentGame['userPresences'][0]['userPresenceType'] != 2:
            print("Clearing activity")
            RPC.clear_activity()
            partyId = None
            await asyncio.sleep(10)
            continue

        currentGame = currentGame['userPresences'][0]
        partyId = random.randint(0, 100000) if (currentGame['placeId'] == None and not partyId) else currentGame['placeId']
        print("Setting activity")
        RPC.set_activity(state=currentGame['lastLocation'], party_id=str(currentGame['placeId']), party_size=[1,20], join=str(currentGame['placeId']) + "i" + str(currentGame['gameId']))

        await asyncio.sleep(10)

RPC.sock_reader.feed_data = RPC.on_event
RPC.loop.create_task(ActivityLoop())
RPC.loop.run_forever()