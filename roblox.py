import browser_cookie3 as bc
import glob
import json
import math
import os
import re
import requests
import time
import urllib
import winreg
from pprint import pprint

JSONDecoder = json.JSONDecoder()

class ROBLOXClient:

    def GetLatestRobloxExe(self):
        reg = winreg.ConnectRegistry(None, winreg.HKEY_CLASSES_ROOT)
        key = winreg.OpenKey(reg, "roblox-player\\DefaultIcon")
        location = winreg.QueryValue(key, '').replace('RobloxPlayerLauncher', 'RobloxPlayerBeta')
        winreg.CloseKey(key)
        return location

    def JoinGame(self, gameUrl=None, gameId=None, serverId=None):
        gameId = gameId if gameId != None else re.search("\/games\/(\d+)", gameUrl).group(1)
        gameUrl = gameUrl if gameUrl != None else "https://www.roblox.com/games/" + gameId
        append = "Job^&placeId=%s^&gameId=%s" % (gameId, serverId) if serverId != None else "^&placeId=" + str(gameId)
        
        headers = {"Connection":"keep-alive", "RBX-For-Gameauth":"true", "Referer":gameUrl, "Host":"www.roblox.com"}
        response = self.session.get("https://www.roblox.com/game-auth/getauthticket", headers=headers)

        # Inform server we're joining
        self.session.post("https://assetgame.roblox.com/game/report-event?name=GameLaunchAttempt_Win32", headers=headers)
        self.session.post("https://assetgame.roblox.com/game/report-event?name=GameLaunchAttempt_Win32_Protocol", headers=headers)

        if response.status_code == 200:
            ticket = response.text
            # os.system("\"" + self.robloxPath + "\" roblox-player:1+launchmode:play+gameinfo:" + ticket + "+launchtime=" + str(math.ceil(time.time())) + "+placelauncherurl:" + urllib.parse.quote("https://assetgame.roblox.com/game/PlaceLauncher.ashx?request=RequestGame" + append + "&isPlayTogetherGame=false") + "+robloxLocale:en_us+gameLocale:en_us")
            os.system("\"" + self.robloxPath + "\" --play -a https://www.roblox.com/Login/Negotiate.ashx -t " + ticket + " -j " + "https://assetgame.roblox.com/game/PlaceLauncher.ashx?request=RequestGame" + append + "^&isPlayTogetherGame=false" + " --launchtime=" + str(math.ceil(time.time())) + " --rloc en_us --gloc en_us")
            self.session.post("https://www.roblox.com/game/increment-play-count", headers=headers)
            self.session.post("https://assetgame.roblox.com/game/report-event?name=GameLaunchSuccessWeb_Win32", headers=headers)
            self.session.post("https://assetgame.roblox.com/game/report-event?name=GameLaunchSuccessWeb_Win32_Protocol", headers=headers)
            return True
        else:
            return response.status_code

    def VerificationProcess(self, responseData, username):
        verificationCode = input("A verification code has been sent to your %s. Please input it here: " % (responseData['twoStepVerificationData']['mediaType'].lower()))
        ticket = responseData['twoStepVerificationData']['ticket']
        vrfResponse = self.session.post("https://auth.roblox.com/v2/twostepverification/verify", data={"actionType":"Login", "code":verificationCode, "rememberDevice":True, "ticket":ticket, "username":username}, headers={'X-CSRF-TOKEN':self.token})
        if vrfResponse.status_code == 403:
            self.VerificationProcess()
        elif vrfResponse.status_code == 400:
            print("Wrong code!")
            self.VerificationProcess()

    def login(self, username, password):
        response = self.session.post("https://auth.roblox.com/v2/login", json={"ctype":"Username", "cvalue":username, "password":password}, headers={'X-CSRF-TOKEN':self.token})
        responseData = response.json()
        if response.status_code == 200:
            self.token = response.headers['X-CSRF-TOKEN']
            if responseData.get('twoStepVerificationData'):
                self.VerificationProcess(responseData, username)
        elif response.status_code == 403:
            self.token = response.headers['X-CSRF-TOKEN']
            self.login(username, password)
        else:
            print(response.status_code)

    def GetAllProcesses(self):
        processes = os.popen("wmic path win32_process get name, commandline /VALUE").read()
        return processes

    def IsRobloxRunning(self):
        processList = self.processes.GetAllProcesses()
        return re.search("RobloxPlayerBeta.exe", processList) != None

    def GetGameInfoFromProcess(self):
        processList = self.processes.GetAllProcesses()
        line = re.search("RobloxPlayerBeta.exe[^\n]+", processList)
        match = re.search(";placeId=(\d+)", line)

        if not match:
            return False
        
        launchTime = re.search("--launchtime=(\d+)", line).group(1)
        gameId = match.group(1)

        if not gameId:
            return False

        gameInfoRequest = self.session.get("https://games.roblox.com/v1/games/multiget-place-details?placeIds=" + gameId)

        if gameInfoRequest.status_code != 200:
            print(gameInfoRequest.status_code)
            return False

        return [gameInfoRequest.json(), launchTime, ]

    def GetCurrentGameInfo(self):
        presenceRequest = self.session.post("https://presence.roblox.com/v1/presence/users", json={'userIds': [self.userId]})
        if presenceRequest.status_code != 200:
            print(presenceRequest.status_code)
            return False
        return presenceRequest.json()

    def __init__(self, cookie=None, username=None, password=None, useBrowserCookie=None):
        self.token = None
        self.processes = Processes()

        self.session = requests.Session()
        self.session.headers.update({'User-Agent':"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"})
        self.robloxPath = self.GetLatestRobloxExe()
        if cookie:
            self.session.cookies = cookie
            request = self.session.get("https://assetgame.roblox.com/Game/GetCurrentUser.ashx")
            self.userId = request.text
        elif useBrowserCookie:
            useBrowserCookie = useBrowserCookie.lower()
            if useBrowserCookie == "chrome":
                client = ROBLOXClient(cookie=bc.chrome(domain_name=".roblox.com"))
            elif useBrowserCookie == "firefox":
                client = ROBLOXClient(cookie=bc.firefox(domain_name=".roblox.com"))
            else:
                client = ROBLOXClient(cookie=bc.load(domain_name=".roblox.com"))
        elif username and password:
            self.login(username, password)

class Processes:
    def __init__(self):
        self.currentProcesses = []

    def GetAllProcesses(self):
        processes = os.popen("wmic path win32_process get name, commandline /VALUE").read()
        return processes