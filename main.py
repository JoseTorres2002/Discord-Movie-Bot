from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_response

# Load token from somewhere safe make it final
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

# Bot Set up
intents: Intents = Intents.default()
intents.message_content = True # NOQA
client: Client = Client(intents=intents)

# Start up
@client.event
async def on_ready() -> None:
    channel = client.get_channel(1337242056946487339)  # Replace with your channel ID
    if channel:
        await channel.send("I am ready to recommend movies. If you need a list of commands type 'help'.")  # Send the "Active" message in the chat

# Handling incoming messages
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    #extracts the contents of the mssg
    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    # logs the mssg
    print(f'[{channel}]{username}: "{user_message}"')

    # Unique user ID for watchlist management
    user_id = str(message.author.id)

    # Get the response using the correct arguments
    try:
        response = get_response(user_id, user_message)
        await message.channel.send(response)

    except Exception as e:
        print(f"Error sending message: {e}")

# Main entry point
def main() -> None:
    client.run(token = TOKEN)

if __name__ == '__main__' :
    main()


