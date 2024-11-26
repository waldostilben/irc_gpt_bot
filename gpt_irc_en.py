import sys
from openai import OpenAI
import socket
import time
import re
import unicodedata

# Configure OpenAI API key
api_key = "sk-proj-... [YOUR OPENAI API KEY HERE]"  # Replace with your API key

client = OpenAI(api_key=api_key)

def clean_text(text):
    """
    Removes problematic characters while preserving accented characters.
    Normalizes and limits the text to 400 characters.
    """
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[^\x20-\x7E\x80-\xFF]", "", text)
    return text[:400]

def get_response(question):
    """
    Sends a question to ChatGPT and returns a cleaned response.
    """
    try:
        print(f"[LOG] Question sent to GPT: {question}")
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Reply with a short message no longer than 400 characters."},
                {"role": "user", "content": question}
            ],
            model="gpt-4o",
        )
        response = chat_completion.choices[0].message.content
        print(f"[LOG] Response received from GPT: {response}")
        return clean_text(response)
    except Exception as e:
        return f"Error querying the API: {e}"

# IRC server configuration
irc_server = sys.argv[1]  # IRC server passed as an argument
irc_port = 6667  # Default IRC port
irc_nickname = "BotNickName"  # Bot's nickname on IRC
irc_realname = "BotRealName"  # Real name for IRC registration
nickserv_password = "BotPassword"  # NickServ authentication password

# List to store channels the bot is monitoring
monitored_channels = []

try:
    # Establish a connection to the IRC server
    irc_socket = socket.create_connection((irc_server, irc_port))
    irc_socket.send(f"NICK {irc_nickname}\r\n".encode("utf-8"))  # Set nickname on the server
    irc_socket.send(f"USER {irc_nickname} 0 * :{irc_realname}\r\n".encode("utf-8"))  # Register user

    authenticated = False  # Flag to check if the bot authenticated with NickServ
    who_sent = False  # Flag to track if the WHO command has been sent

    while True:
        # Receive data from the IRC server
        data = irc_socket.recv(512)
        try:
            decoded_data = data.decode("utf-8").strip()
        except UnicodeDecodeError:
            decoded_data = data.decode("ISO-8859-1").strip()

        print(f"[LOG] Data received from IRC server: {decoded_data}")

        # Respond to server PING to keep the connection alive
        if decoded_data.startswith("PING"):
            irc_socket.send(f"PONG {decoded_data.split()[1]}\r\n".encode("utf-8"))

        # Authenticate with NickServ using the provided password
        if "NickServ" in decoded_data and "IDENTIFY" in decoded_data and not authenticated:
            print(f"[LOG] Authenticating with NickServ using password: {nickserv_password}")
            irc_socket.send(f"PRIVMSG NickServ :IDENTIFY {nickserv_password}\r\n".encode("utf-8"))
            authenticated = True

        # After authentication, send the WHO command to check channels
        if authenticated and not who_sent:
            time.sleep(10)  # Wait to ensure the server is ready
            print("[LOG] Sending WHO command to discover channels.")
            irc_socket.send(f"WHO {irc_nickname}\r\n".encode("utf-8"))
            who_sent = True

        # Process WHO command response to detect channels
        if "352" in decoded_data:  # Standard WHO response
            match_who = re.search(rf"352 .* #(\S+)", decoded_data)
            if match_who:
                channel = f"#{match_who.group(1)}"
                if channel not in monitored_channels:
                    monitored_channels.append(channel)  # Add detected channel to the list
                    print(f"[LOG] Channel detected and added to the list: {channel}")

        # Process private commands sent to the bot
        match_private = re.search(rf":(.+?)!.+? PRIVMSG {irc_nickname} :(.+)", decoded_data)
        if match_private:
            user = match_private.group(1)  # Name of the sender
            message = match_private.group(2).strip()  # Received message
            print(f"[LOG] Private command received from {user}: {message}")

            if message.startswith(".join"):
                # Join channels specified in the .join command
                new_channels = message[6:].strip().split()
                for channel in new_channels:
                    if channel not in monitored_channels:
                        monitored_channels.append(channel)  # Add channel to the list
                        print(f"[LOG] Joining channel: {channel}")
                        irc_socket.send(f"JOIN {channel}\r\n".encode("utf-8"))
                irc_socket.send(f"PRIVMSG {user} :Joining channels: {', '.join(new_channels)}\r\n".encode("utf-8"))

        # Process messages in monitored channels
        for channel in monitored_channels:
            if f"PRIVMSG {channel}" in decoded_data:
                match_channel = re.search(rf":(.+?)!.+? PRIVMSG {channel} :(.+)", decoded_data)
                if match_channel:
                    user = match_channel.group(1)  # Name of the user who sent the message
                    message = match_channel.group(2).strip()  # Content of the message
                    print(f"[LOG] Message received from {user} in channel {channel}: {message}")

                    if message.startswith(".gpt "):
                        # Process questions sent to the bot using .gpt
                        question = message[5:].strip()
                        response = get_response(question)
                        irc_socket.send(f"PRIVMSG {channel} :{user}: {response}\r\n".encode("utf-8"))
                        print(f"[LOG] Response sent to {user} in channel {channel}: {response}")

except Exception as e:
    print(f"Error: {e}")
