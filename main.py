from concurrent.futures import ThreadPoolExecutor
from roblox import ROBLOXClient
from pprint import pprint
from pypresence import Presence, Client
import asyncio
import browser_cookie3 as bc
import time
import random
import re
import rpc
import uuid

partyId = None
maxTrials = 2

RPC = rpc.DiscordIpcClient.for_platform('541669343805833216')
RPC.send({'cmd':'SUBSCRIBE', 'evt':'ACTIVITY_JOIN', 'nonce':str(uuid.uuid4())})
RPC.send({'cmd':'SUBSCRIBE', 'evt':'ACTIVITY_JOIN_REQUEST', 'nonce':str(uuid.uuid4())})
client = ROBLOXClient(cookie=bc.chrome(domain_name=".roblox.com"))

loop = asyncio.get_event_loop()
_executor = ThreadPoolExecutor(1)

async def RPCLoop():
    global partyId
    while True:
        print("Getting message")
        message = await loop.run_in_executor(_executor, RPC.recv)
        message = message[1]

        if message['cmd'] != "DISPATCH":
            await asyncio.sleep(0.5)
            continue

        if message['evt'] == 'ACTIVITY_JOIN':
            contents = message['data']['secret']
            placeId = re.search("(\d+)i", contents).group(1)
            serverId = re.search("i(.+)", contents).group(1)

            client.JoinGame(gameId = placeId, serverId=serverId)

            for i in range(maxTrials):
                print("CHECK")
                if client.IsRobloxRunning():
                    currentGame = client.GetCurrentGameInfo()
                    SetActivity(str(currentGame['lastLocation']), currentGame['placeId'], currentGame['gameId'])
                    await asyncio.sleep(3)
            partyId = placeId
        elif message['evt'] == 'ACTIVITY_JOIN_REQUEST':
            userId = message['data']['user']['id']
            RPC.send({'nonce':str(uuid.uuid4()), 'cmd':'SEND_ACTIVITY_JOIN_INVITE', 'args':{'user_id':userId}})

def SetActivity(gameName, placeId, gameId):
    RPC.set_activity({
        "state":gameName,
        "party": {
            "id":str(partyId),
            "size":[1,2],
        },
        "secrets": {
            "join": str(placeId) + "i" + str(gameId)
        }
    })
    return

async def ActivityLoop():
    global partyId
    while True:
        print("Finding game")
        currentGame = client.GetCurrentGameInfo()
        if not currentGame or currentGame['userPresences'][0]['userPresenceType'] != 2:
            # RPC.close()
            partyId = None
            await asyncio.sleep(20)
            continue

        currentGame = currentGame['userPresences'][0]
        partyId = random.randint(0, 100000) if (currentGame['placeId'] == None and not partyId) else currentGame['placeId']
        print("Setting activity!")
        SetActivity(str(currentGame['lastLocation']), currentGame['placeId'], currentGame['gameId'])

        await asyncio.sleep(20)

loop.run_until_complete(asyncio.gather(RPCLoop(), ActivityLoop()))

# client.JoinGame(gameUrl="https://www.roblox.com/games/261290060/Terminal-Railways#!/game-instances", serverId="3d6e5b16-bf89-49bc-b97e-411e8cc6abc7")