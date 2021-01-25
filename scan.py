import configparser
import json
import asyncio

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.types import (
    PeerChannel
)

# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini")

# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

api_hash = str(api_hash)

phone = config['Telegram']['phone']
username = config['Telegram']['username']

eIDsFile = open('telegramq.txt', 'r')
eIDs = eIDsFile.readlines()
print("ECount: ", len(eIDs))

# Create the client and connect
client = TelegramClient(username, api_id, api_hash)

async def main(phone):
    await client.start()
    print("Client Created")
    # Ensure you're authorized
    if await client.is_user_authorized() == False:
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    me = await client.get_me()

    for eID in eIDs:
        user_input_channel = eID
        try:
            if user_input_channel.isdigit():
                entity = PeerChannel(int(user_input_channel))
            else:
                entity = user_input_channel

        except:    
            print("failed to load: ", eID)
            continue

        try:
            my_channel = await client.get_entity(entity)

            offset = 0
            limit = 100
            all_participants = []

            while True:
                participants = await client(GetParticipantsRequest(
                    my_channel, ChannelParticipantsSearch(''), offset, limit,
                    hash=0
                ))
                if not participants.users:
                    break
                all_participants.extend(participants.users)
                offset += len(participants.users)
                sleep(3) #Hopefully prevent 420 FLOOD Error

            all_user_details = []
            for participant in all_participants:
                all_user_details.append(
                    {"id": participant.id, "first_name": participant.first_name, "last_name": participant.last_name,
                     "user": participant.username, "phone": participant.phone, "is_bot": participant.bot})

            with open('users/user_data_' + eID.replace("https://t.me/", "").replace("\n","") + '.json', 'w') as outfile:
                json.dump(all_user_details, outfile)

        except Exception as err:
            print(err)
            print("failed to parse line", eID)

with client:
    client.loop.run_until_complete(main(phone))
