# CREATED BY EXPOOKY :)

import discord, json, requests, httpx, base64
from json import loads
from discord import Embed
from discord.ext import commands
import random
import httpx

bot = discord.Bot(status=discord.Status.online, intents=discord.Intents.all())

settings = json.load(open("botSettings.json", encoding="utf-8"))

@bot.event
async def on_ready():
    activity = discord.Game(name="Bot", type=2)
    print(">> Boost Bot is now ready to use, you may now proceed.")

ge = ("pastebin.pl")

def parse_embed_json(json_file):
    embeds_json = loads(json_file)['embeds']

    for embed_json in embeds_json:
        embed = Embed().from_dict(embed_json)
        yield embed

def vAdmin(ctx):
    return str(ctx.author.id) in settings["botAdminId"]

def removeToken(token: str):
    with open('freshTokens.txt', "r") as f:
        Tokens = f.read().split("\n")
        for t in Tokens:
            if len(t) < 5 or t == token:
                Tokens.remove(t)
        open("freshTokens.txt", "w").write("\n".join(Tokens))

def getSuperProperties():
    properties = '''{"os":"Windows","browser":"Chrome","device":"","system_locale":"en-GB","browser_user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36","browser_version":"95.0.4638.54","os_version":"10","referrer":"","referring_domain":"","referrer_current":"","referring_domain_current":"","release_channel":"stable","client_build_number":102113,"client_event_source":null}'''
    properties = base64.b64encode(properties.encode()).decode()
    return properties

def getFingerprint(s):
    try:
        fingerprint = s.get(f"https://discord.com/api/v9/experiments", timeout=5).json()["fingerprint"]
        return fingerprint
    except Exception as e:
        return "Error"

def getCookies(s, url):
    try:
        cookieinfo = s.get(url, timeout=5).cookies
        dcf = str(cookieinfo).split('__dcfduid=')[1].split(' ')[0]
        sdc = str(cookieinfo).split('__sdcfduid=')[1].split(' ')[0]
        return dcf, sdc
    except:
        return "", ""

def getProxy():
    return None

def getHeaders(token):
    while True:
        s = httpx.Client(proxies=getProxy())
        dcf, sdc = getCookies(s, "https://discord.com/")
        fingerprint = getFingerprint(s)
        if fingerprint != "Error":
            break

    super_properties = getSuperProperties()
    headers = {
        'authority': 'discord.com',
        'method': 'POST',
        'path': '/api/v9/users/@me/channels',
        'scheme': 'https',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en-US',
        'authorization': token,
        'cookie': f'__dcfduid={dcf}; __sdcfduid={sdc}',
        'origin': 'https://discord.com',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',

        'x-debug-options': 'bugReporterEnabled',
        'x-fingerprint': fingerprint,
        'x-super-properties': super_properties,
    }

    return s, headers

def findToken(token):
    if ':' in token:
        token_chosen = None
        tokensplit = token.split(":")
        for thing in tokensplit:
            if '@' not in thing and '.' in thing and len(
                    thing) > 30:  # trying to detect where the token is, if a user pastes email:pass:token (and we dont know the order)
                token_chosen = thing
                break
        if token_chosen == None:
            print(f"Error finding token")
            return None
        else:
            return token_chosen
    else:
        return token

def getAllTokens(filename):
    all_tokens = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            token = line.strip()
            token = findToken(token)
            if token != None:
                all_tokens.append(token)
    return all_tokens

def validateTokens(s, headers):
    check = s.get(f"https://discord.com/api/v9/users/@me", headers=headers)
    if check.status_code == 200:
        profile_name = check.json()["username"]
        profile_discrim = check.json()["discriminator"]
        profile_of_user = f"{profile_name}#{profile_discrim}"
        return profile_of_user
    else:
        return False

def memberGate(s, token, headers, profile, invite, server_id):
    outcome = False
    try:
        member_gate = s.get(
            f"https://discord.com/api/v9/guilds/{server_id}/member-verification?with_guild=false&invite_code={invite}",
            headers=headers)
        if member_gate.status_code != 200:
            return outcome
        accept_rules_data = member_gate.json()
        accept_rules_data["response"] = "true"
        accept_member_gate = s.put(f"https://discord.com/api/v9/guilds/{server_id}/requests/@me", headers=headers,
                    json=accept_rules_data)
        if accept_member_gate.status_code == 201:
            outcome = True

    except:
        pass

    return outcome

def joinServer(s, token, headers, profile, invite):
    join_outcome = False
    server_id = None
    try:
        headers["content-type"] = 'application/json'

        for i in range(15):
            try:
                createTask = httpx.post("https://api.capmonster.cloud/createTask", json={
                    "clientKey": settings["capmonsterKey"],
                    "task": {
                        "type": "HCaptchaTaskProxyless",
                        "websiteURL": "https://discord.com/channels/@me",
                        "websiteKey": "76edd89a-a91d-4140-9591-ff311e104059"
                    }
                }).json()["taskId"]
                print(f">> Captcha Task Created")
                getResults = {}
                getResults["status"] = "processing"
                while getResults["status"] == "processing":
                    getResults = httpx.post("https://api.capmonster.cloud/getTaskResult", json={
                        "clientKey": settings["capmonsterKey"],
                        "taskId": createTask
                    }).json()
                solution = getResults["solution"]["gRecaptchaResponse"]
                print(f">> Captcha Solved")
                join_server = s.post(f"https://discord.com/api/v9/invites/{invite}", headers=headers, json={
                    "captcha_key": solution
                })
                break
            except:
                pass
        server_invite = invite
        if join_server.status_code == 200:
            join_outcome = True
            server_name = join_server.json()["guild"]["name"]
            server_id = join_server.json()["guild"]["id"]
            print(f">> {profile} > {server_invite}")
    except:
        pass
    return join_outcome, server_id

def doBoost(s, token, headers, profile, server_id, boost_id):
    boost_data = {"user_premium_guild_subscription_slot_ids": [f"{boost_id}"]}
    headers["content-length"] = str(len(str(boost_data)))
    headers["content-type"] = 'application/json'

    boosted = s.put(f"https://discord.com/api/v9/guilds/{server_id}/premium/subscriptions", json=boost_data,
                    headers=headers)
    if boosted.status_code == 201:
        return True
    else:
        return False

def getInvite():
    while True:
        print(f"Server invite?", end="")
        invite = input(" > ").replace("//", "")
        if "/invite/" in invite:
            invite = invite.split("/invite/")[1]
        elif "/" in invite:
            invite = invite.split("/")[1]
        dataabotinvite = httpx.get(f"https://discord.com/api/v9/invites/{invite}").text
        if '{"message": "Unknown Invite", "code": 10006}' in dataabotinvite:
            print(f">> Discord.gg/{invite} is invalid invite link")
        else:
            print(f">> Discord.gg/{invite} is valid invite link")
            break
    return invite

def getItems(item):
    s = item[0]
    token = item[1]
    headers = item[2]
    profile = item[3]
    return s, token, headers, profile

def booost(invite: str, amount: int):
    if amount %2!=0:
        amount +=1
    tokens = getAllTokens("freshTokens.txt")
    all_data = []
    tokens_checked = 0
    actually_valid = 0
    boosts_done = 0
    for token in tokens:
        s, headers = getHeaders(token)
        profile = validateTokens(s, headers)
        tokens_checked += 1
        if profile != False:
            actually_valid += 1
            data_piece = [s, token, headers, profile]
            all_data.append(data_piece)
            print(f">> {profile}")
        else:
            pass
    for data in all_data:
        if boosts_done >= amount:
            return
        s, token, headers, profile = getItems(data)
        boost_data = s.get(f"https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots", headers=headers)
        if boost_data.status_code == 200:
            if len(boost_data.json()) != 0:
                join_outcome, server_id = joinServer(s, token, headers, profile, invite)
                if join_outcome:
                    for boost in boost_data.json():
                        if boosts_done >= amount:
                            removeToken(token)
                        boost_id = boost["id"]
                        boosted = doBoost(s, token, headers, profile, server_id, boost_id)
                        if boosted:
                            print(f">> {profile} BOOSTED {invite}")
                            boosts_done += 1
                        else:
                            print(f">> USER {profile}'s BOOST IS ALREADY USED")
                    removeToken(token)
                else:
                    print(f">> {profile} CAN'T JOIN {invite}")
            else:
                removeToken(token)
                print(f">> [{profile}] THIS USER HAS NO NITRO SUBSCRIPTION. BOOST FAILED")

@bot.slash_command(guild_ids=[settings["guildID"]], name="checkstock", description="View Stocks")
async def stock(ctx: discord.ApplicationContext):
        if not vAdmin(ctx):
            print(f">> An Unauthorized User used the command (/stock)")
            return await ctx.respond("**`You don't have enough permissions to use this command.`**")
        print(f">> /stock has been used")
        return await ctx.respond(f"You Have **{len(open('freshTokens.txt', encoding='utf-8').read().splitlines()*2)}** Available Boosts")

@bot.slash_command(guild_ids=[settings["guildID"]], name="addtokens", description="Add Tokens")
async def restock(ctx: discord.ApplicationContext, code: discord.Option(str, f"Make sure to add an additional line on {ge} without any letters so your token can stack", required=True,)):
    if not vAdmin(ctx):
        print(f">> An Unauthorized User used the command (/restock)")
        return await ctx.respond("**`You don't have enough permissions to use this command.`**")
    print(f">> /restock has been used")
    await ctx.respond("**⌛  Getting Tokens...**")
    url = f'https://pastebin.pl/view/raw/{code}'
    paste = requests.get(url)
    content = paste.text
    with open("freshTokens.txt", "a", encoding="utf-8") as file:
        file.write(f'{content}')
        file.close()
    return await ctx.edit(content=f"**\n✅ Tokens added Successfully.** \n\n You now have a total of **{len(open('freshTokens.txt', encoding='utf-8').read().splitlines())}** Token(s) or **{len(open('freshTokens.txt', encoding='utf-8').read().splitlines()*2)}** Boosts")

@bot.slash_command(guild_ids=[settings["guildID"]], name="removetokens", description="Remove Current Tokens")
async def cstock(ctx: discord.ApplicationContext):
    if not vAdmin(ctx):
        print(f">> An Unauthorized User used the command (/removetokens)")
        return await ctx.respond("**`You don't have enough permissions to use this command.`**")
    print(f">> /removetokens has been used")
    await ctx.respond("**⌛  Removing Tokens...**")
    with open("freshTokens.txt", "a", encoding="utf-8") as file:
        file.truncate(0)
        file.close()
    return await ctx.edit(content=f"\n**✅ Tokens removed Successfully.** \n\n You now have a total of **{len(open('freshTokens.txt', encoding='utf-8').read().splitlines())}** Token(s)")

@bot.slash_command(guild_ids=[settings["guildID"]], name="boost", description="Boost a Server")
async def boost(ctx: discord.ApplicationContext,
                invitecode: discord.Option(str, "Discord Server Invite Link/Code", required=True),
                amount: discord.Option(int, "Amount of Boosts", required=True)):
    if not vAdmin(ctx):
        print(f">> /boost has been used")
        return await ctx.respond("**`You don't have enough permissions to use this command.`**")
    print(f">> /boost has been used")
    await ctx.respond("**⌛ Boosting the server...**")

    INVITE = invitecode.replace("//", "")
    if "/invite/" in INVITE:
        INVITE = INVITE.split("/invite/")[1]

    elif "/" in INVITE:
        INVITE = INVITE.split("/")[1]

    dataabotinvite = httpx.get(f"https://discord.com/api/v9/invites/{INVITE}").text

    if '{"message": "Unknown Invite", "code": 10006}' in dataabotinvite:
        return await ctx.edit("❌  The invitation link/code you provided is invalid and the operation will be terminated.")
    else:
        print(f">> VALID SERVER discord.gg/{INVITE}")

    booost(INVITE, amount)
    
    return await ctx.edit("**Boost Success!**")

bot.run(settings["botToken"])