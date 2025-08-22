import time
import requests
import stashconnect
import json
import cohere
import urllib.parse

# === LOGIN DATEN ===
EMAIL = "YOUR_EMAIL_HERE"  # Set your email here
PASSWORD = "YOUR_PASSWORD_HERE"  # Set your password here
ENCRYPTION_PASSWORD = "YOURENCRYPTION_PASSWORD_HERE"  # Set your encryption password here

# === CHANNELS ===
TARGET_CONVERSATIONS = [
    "000000",  # Replace with your target conversation ID
]

client = stashconnect.Client(
    email=EMAIL,
    password=PASSWORD,
    encryption_password=ENCRYPTION_PASSWORD
)

# --- Bot State ---
seen = set()
MENU_MARKER = "_menu_marker_"

ASCII_MENU = r"""
_
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║       
║ @@@@@@@@  @@@       @@@  @@@  @@@  @@@  @@@@@@@   @@@@@@@@  @@@@@@@        ║
║ @@@@@@@@  @@@       @@@  @@@  @@@@ @@@  @@@@@@@@  @@@@@@@@  @@@@@@@@       ║
║ @@!       @@!       @@!  @@@  @@!@!@@@  @@!  @@@  @@!       @@!  @@@       ║
║ !@!       !@!       !@!  @!@  !@!!@!@!  !@!  @!@  !@!       !@!  @!@       ║
║ @!!!:!    @!!       @!@  !@!  @!@ !!@!  @!@  !@!  @!!!:!    @!@!!@!        ║
║ !!!!!:    !!!       !@!  !!!  !@!  !!!  !@!  !!!  !!!!!:    !!@!@!         ║
║ !!:       !!:       !!:  !!!  !!:  !!!  !!:  !!!  !!:       !!: :!!        ║
║ :!:        :!:      :!:  !:!  :!:  !:!  :!:  !:!  :!:       :!:  !:!       ║
║  ::        :: ::::  ::::: ::   ::   ::   :::: ::   :: ::::  ::   :::       ║
║  :        : :: : :   : :  :   ::    :   :: :  :   : :: ::    :   : :       ║
║                                                                            ║ 
║                                                                            ║ 
║                                                                            ║ 
║                                                                            ║ 
║----------------------------------------------------------------------------║ 
║                                                                            ║ 
║                                                                            ║                          
║   Commands:                                                                ║
║   poll option1 option2 ...                                                 ║
║   ai frage                                                                 ║
║   tiktaktoe  - Play tik tak toe                                            ║
║   ping   - Secret                                                          ║ 
║   status - Stats                                                           ║
║   menu /  help  - Display this!                                            ║
║                                                                            ║    
║                                                                            ║
║                                                                            ║
║                                                                            ║
║                                                                            ║                   
║      __ _____  (_)_ __                                                     ║ 
║     / // / _ \/ /\ \ /                                                     ║                                                         
║     \_,_/_//_/_//_\_\                                                      ║ 
║                                                                            ║ 
║     visit xtchitopx.de                                                     ║
║     github.com/tchitop                                                     ║
║     twitch.tv/xtchitopx                                                    ║
║     discord.gg/rootunix                                                    ║
║     youtube.com/@rootunix                                                  ║
║     whatsapp: +4915679597138                                               ║
║                                                                            ║ 
║                                                                            ║
║----------------------------------------------------------------------------║                                 
╚════════════════════════════════════════════════════════════════════════════╝

"""

COHERE_API_KEY = "YOUR_COHERE_API_KEY_HERE"  # Set your Cohere API key here DOESNT WORK BTW
co = cohere.Client(COHERE_API_KEY)

def build_poll_link(title, options):
    # URL encode
    params = {"title": title}
    for i, opt in enumerate(options, start=1):
        params[f"op{i}"] = opt
    return POLL_BASE_URL + "?" + urllib.parse.urlencode(params)

def ai_answer(prompt: str) -> str:
    try:
        response = co.chat(
            model="command-xlarge-nightly",  # aktuell verfügbar
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ AI-Fehler: {e}"
    
def normalize_msgs(msgs_raw):
    if msgs_raw is None:
        return []
    if isinstance(msgs_raw, dict):
        if "messages" in msgs_raw:
            return msgs_raw["messages"]
        if "data" in msgs_raw:
            return msgs_raw["data"]
        return list(msgs_raw.values())
    if isinstance(msgs_raw, (list, tuple)):
        return msgs_raw
    return [msgs_raw]


def extract_id_content(m):
    mid = None
    content = None
    if hasattr(m, "id"):
        mid = getattr(m, "id")
    if hasattr(m, "content"):
        content = getattr(m, "content")
    if isinstance(m, dict):
        mid = mid or m.get("id") or m.get("message_id") or m.get("mid")
        content = content or m.get("content") or m.get("text") or m.get("body")
    return mid, content






# Hauptschleife
while True:
    try:
        for conv_id in TARGET_CONVERSATIONS:
            try:
                gen = client.messages.get_messages(conv_id)
                msgs_raw = list(gen)
            except Exception:
                try:
                    msgs_raw = client.messages.infos(conv_id)
                except Exception:
                    msgs_raw = []

            msgs = normalize_msgs(msgs_raw)

            for m in msgs:
                mid, content = extract_id_content(m)
                if not mid or content is None:
                    continue
                if mid in seen:
                    continue
                seen.add(mid)

                text = str(content).strip()



                print("Nachricht erkannt:", repr(text)[:200])

                if text in ("!menu", "!help"):
                    client.messages.send(conv_id, f"```{ASCII_MENU}```")
                    continue

                if text.startswith("!poll "):
                    options = text[len("!poll "):].strip().split()
                    if len(options) < 2:
                        client.messages.send(conv_id, "❌ Bitte mindestens 2 Optionen angeben.")
                        continue

                    # Generiere Link
                    poll_link = build_poll_link("Umfrage", options)
                    client.messages.send(conv_id, f"📊 Umfrage-Link: {poll_link}\nTitel: Umfrage | Optionen: {', '.join(options)}")
                    
                    title = parts[0].strip()
                    options = [p.strip() for p in parts[1:]]
                    client.messages.send(conv_id, f"📊 Umfrage-Link: {poll_link}")
                    continue

                if text == "!ping":
                    client.messages.send(conv_id, "🏓 Pong!")
                    continue
                if text == "!tiktaktoe":
                    client.messages.send(conv_id, "Starte tiktaktoe.")
                    TIKTAKTOE = stashconnect.TikTakToe(client, conv_id)
                    TIKTAKTOE.start()
                    continue
                if text.startswith("!ai "):
                    frage = text[len("!ai "):].strip()
                    if not frage:
                        client.messages.send(conv_id, "❌ Bitte eine Frage nach dem Befehl angeben.")
                        continue
                    antwort = ai_answer(frage)
                    client.messages.send(conv_id, f"🤖 {antwort}")
                    continue

            time.sleep(0.5)

        time.sleep(2)

    except KeyboardInterrupt:
        print("Bot beendet.")
        break
    except Exception as e:
        print("Fehler in der Hauptschleife:", e)
        time.sleep(5)