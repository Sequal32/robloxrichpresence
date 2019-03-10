import requests
from roblox import ROBLOXClient

client = ROBLOXClient(useBrowserCookie=input("What browser do you use for ROBLOX? "), requireUserId=False)
username = input("Username of the player to look for: ")
gameid = input("PlaceId of the game to search in: ")

userdata = requests.get("https://api.roblox.com/users/get-by-username?username=" + username).json()
if userdata.get("success"):
    print("Invalid Username!")
    exit()
userid = str(userdata["Id"])

image = requests.get("https://www.roblox.com/headshot-thumbnail/image?userId="+userid+"&width=48&height=48&format=png")
serverid = None

index = 0
found = False
endoftheline = False

while not found and not endoftheline:

    data = client.GetRequest("https://www.roblox.com/games/getgameinstancesjson?placeId=%s&startIndex=%d" % (gameid, index)).json()
    collectionsize = len(data['Collection'])
    index = index+collectionsize
    endoftheline = True if collectionsize == 0 else False
    print("Searching servers from " + str(index) + " Collection Size: " + str(collectionsize))
    for server in data['Collection']:
        for player in server['CurrentPlayers']:
            if player['Thumbnail']['Url'] == image.url:
                serverid = server['Guid']
                found = True;
                print("Player found! Joining server " + serverid)

if serverid != None:
    client.JoinGame(gameId=gameid, serverId=serverid)
