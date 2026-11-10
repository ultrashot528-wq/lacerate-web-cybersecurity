#!/usr/bin/env python3
import asyncio
import httpx
import subprocess
import pyfiglet
import aiofiles
import json
import random
import string
import os
import sys
import readline

if os.name == 'nt':
    print("you're using windows, so you are not invited")    
    sys.exit(1)
def clear():
    subprocess.run("clear")

clear()
print("note: this runs faster in a free threaded python build")

# manual interaction, as is with curl
# requester() is basically the heart of this whole thing
async def requester(website):
    if not website.startswith(("https://", "http://")):
        print("invalid")
        return None
    print("valid")
         
    print("how many times to send?")
    try:
        timetosend = int(input("rtimes > "))
    except ValueError:
        print("use a number")
        return None
             
    print("what type of request?")
    print('''       1: GET
       2: POST
       3: PUT
       4: PATCH''')
    type_of_request = input("rtype > ")

    method_map = {"1": "GET", "2": "POST", "3": "PUT", "4": "PATCH"}
    http_method = method_map.get(type_of_request, "GET")

    print('''         1: See just status code
          2: Show FULL response
          3: Throw response into a json
        ''')
    verbosity = input("rshow > ")
    print(f"sending {http_method} requests...")
         
    async with httpx.AsyncClient() as client:
        last_response = None
        for i in range(0, timetosend):
            try:
                response = await client.request(http_method, website)
                print(f"Status: {response.status_code}")
                last_response = response
                             
                if verbosity == '2':
                    print("Big text coming up in 3 seconds")
                    await asyncio.sleep(3)
                    print(f"{response.text}")
                                 
                elif verbosity == '3':
                    clean_website = website.replace("http://", "").replace("https://", "").replace("/", "_")
                    print(f"Saving to json under the name {clean_website}_laceration.json")
                    try:
                        data = response.json()
                    except Exception:
                        data = {"url": website, "content": response.text}
                                             
                    async with aiofiles.open(f"{clean_website}_laceration.json", mode="w") as file:
                        await file.write(json.dumps(data, indent=4))
            except Exception as e:
                print(f"Network error: {e}")
        return last_response

def randomgen():
    length = random.randint(5, 15)
    pool = string.ascii_lowercase + string.digits
    domain = ''.join(random.choices(pool, k=length))
    tld = random.choice([".com", ".net", ".org", ".io"])
    return f"{domain}{tld}"

async def silent_request(method, url):
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.request(method, url)
            return response
    except httpx.RequestError:
        return None

async def directory_fuzz(website):
    if not website.startswith(("https://", "http://")):
        website = f"http://{website}"

    print("fuzzer")
    wordlist = input("wordlist? put nothing if you want to use the default, big.txt \n fordlist > ").strip()
    wordlist = "big.txt" if wordlist == '' else wordlist # oh my god it looks like i had a stroke
    print(f"reading from {wordlist}")
    
    try:
        async with aiofiles.open(wordlist, "r") as file:
            async with httpx.AsyncClient(timeout=3.0) as client:
    
                print("checking server behavior for soft 404s")
                fake_path = f"{website.rstrip('/')}/laceratesandboxfake123456likenothingisgoingtobenamedthisformanyreasons"
                try:
                    baseline_res = await client.get(fake_path, follow_redirects=False)
                    baseline_length = len(baseline_res.text) if baseline_res.is_success else -1
                    print(f"[*] Baseline 200 body length: {baseline_length} bytes (will filter soft 404 matches)")
                except Exception:
                    baseline_length = -1
                # ------------------------------------

                while True:
                    line = await file.readline()
                    if not line:
                        print("hit the end, your results are in a json") #TODO: ADD A JSON FUNCTION 
                        break
                        
                    directory = line.strip()
                    if not directory or directory.startswith("#"):
                        continue
                        
                    url_with_dir = f"{website}" + "/" + f"{directory}"
                    #TODO: ADD A VERBOSE FUNCTION
                    
                    try:
                        response = await client.get(url_with_dir, follow_redirects=False)
                        
                        if response.is_success:
                            # Filter out soft 404s that match the baseline page length
                            if baseline_length != -1 and len(response.text) == baseline_length:
                                continue
                            print(f"OK: {response.status_code} -> {url_with_dir}")
                        elif response.is_redirect:
                            print(f"REDIRECT: {response.status_code} -> {url_with_dir}")
                        elif response.is_client_error:
                            if response.status_code == 404:
                                # the sheer amount of 404s in fuzzing makes this necessary
                                continue
                            else:
                                print(f"CLIENTERROR: {response.status_code} -> {url_with_dir}")
                        elif response.is_server_error:
                            print(f"SERVERERROR: {response.status_code} -> {url_with_dir}")
                    except httpx.RequestError:
                        pass
                        
        print("fuzzing complete!")
    except Exception as e:
        print(f"Fuzzing error: {e}")

async def request_fuzz():
    try:
        how_many = int(input("how many urls to fuzz? \n rfnum > "))
    except ValueError:
        print("defaulting to 10, perhaps use an integer")
        how_many = 10

    verbose = input("verbose? y/n \n rsay > ").strip().lower()
    print("running...")
         
    for _ in range(how_many):
        httporhttps = random.randint(1, 2)
        base_url = randomgen()
        website = f"http://{base_url}" if httporhttps == 2 else f"https://{base_url}"
                 
        if verbose == 'y':
            print(f"Testing: {website}")
                 
        request = await silent_request("GET", website)
                 
        if request and request.is_success:
            print(f"[{request.status_code}] found live target: {website}")
        elif verbose == 'y':
            if request:
                print(f" -> answered with: {request.status_code}")
            else:
                print(" -> dead/unresolved tld")

RESET = "\033[0m"
BOLD = "\033[1m"
BLUE = "\033[34m"
flavor = random.randint(1, 10)
boring_banner = pyfiglet.figlet_format("LACERATE", font="slant")                                 
cool_banner = f"{boring_banner}{RESET}"
print(f"{BLUE} {cool_banner} {RESET}")
print("help for commands")
# i have matured enough to find match and case a little better than if/elif/else
match flavor:
    case 1:
        print("Lacerate doesn't make any sense in the context of web testing but hey, it's a cool name.")
    case 2:
        print("Perhaps a shell popper can be added?")
    case 3:
        print("dns-fuzz may not have utility on the surface, but trust me--obfuscating traffic is useful")
    case 4:
        print("uh oh, looks like i'm using big.txt from dirb!")
    case 5:
        print("thou shall not pass!!!!!!!")
    case 6:
        print("directory-fuzz is just gobuster, trust me here")
    case 7:
        print("oh you use dirb? recursively remove your root directory...not on your computer.")
    case 8:
        print("LET IT RIDEEEEEEEEEEEEEE")
    case 9:
        print("I used to use Vim to write my code, as with sundown and adversary but I find VSCodium MUCH better. great IDE")
    case 10:
        print("I might build a C2 server, who knows?")
    
print('''\n Commands
request        -> send a request and get the response (interactive)
dns-fuzz       -> fuzz random domains automatically
directory-fuzz -> fuzz random directories automatically
clear          -> clear screen
''')

while True:
    try:
        command = str(input(f"{BLUE} {BOLD} Lacerate > {RESET}")).strip().lower()
        if command == 'request':
            print("requester")
            print("what website")
            website = input("request > ")
            asyncio.run(requester(website))
        elif command == 'clear':
            clear()
        elif command == 'dns-fuzz':
            asyncio.run(request_fuzz())
        elif command == 'directory-fuzz':
            website = input("what website \n febsite > ")
            asyncio.run(directory_fuzz(website))
        elif command in ['help', '?']:
            print('''Commands
            request        -> send a request and get the response (interactive)
            dns-fuzz       -> fuzz random domains automatically
            directory-fuzz -> directory fuzzer with soft-404 finder
            clear          -> clear screen
            help/?         -> this
            exit/quit      -> exit''')
        elif command in ['exit', 'quit']:
            sys.exit(0)
        else:
            print('''Invalid
            request        -> send a request and get the response (interactive)
            dns-fuzz       -> fuzz random domains automatically
            directory-fuzz -> directory fuzzer with soft-404 finder
            help/?         -> show this
            clear          -> clear screen 
            exit/quit      -> exit
            ''')
    except (KeyboardInterrupt, EOFError):
        print("\nExiting...")
        break
