### This is for 4704
from telethon import TelegramClient, events, sync
import json
import os
import asyncio
import time
from datetime import date, datetime
import jsonpickle
import random
import pickle
import abc
from telethon import errors
import sys


from bunch import bunchify

from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (
	PeerChannel,
	Message
)
import telethon.tl.types
import traceback

class SubClient:
	def __init__(self):
		self.queue = []

# some functions to parse json date
class DateTimeEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, datetime):
			return o.isoformat()

		if isinstance(o, bytes):
			return list(o)

		return json.JSONEncoder.default(self, o)


api_id = xxx
api_hash = "xxx"
api_username = "xxx"
api_number = "+xxx"


client = TelegramClient('session_name', api_id, api_hash)

subClientCount = 4
subClients = []


async def main():
	await client.start()
	print("Client Created")
	# Ensure you're authorized
	if await client.is_user_authorized() == False:
		await client.send_code_request(api_number)
		try:
			await client.sign_in(api_number, input('Enter the code: '))
		except SessionPasswordNeededError:
			await client.sign_in(password=input('Password: '))
	


	me = await client.get_me()

	for group_id in open("input.txt", "r").read().splitlines():
	# for group_id in groups:
		print("waiting 30 seconds for next group :)")
		time.sleep(5)

		user_input_channel = group_id
		
		try:
			if user_input_channel.isdigit():
				entity = PeerChannel(int(user_input_channel))
			else:
				entity = user_input_channel

			normGid = group_id.replace("https://t.me/", "").replace("\n","").lower()
			print("parsing: ", normGid)

			try:
				my_channel = await client.get_input_entity(entity)

			except Exception as entityErr:
				print("Channel not found:", entity, entityErr)
				continue
				
			try:
				
				print(my_channel)
				users = []
				messages = []
				i = 0

				messagesToDownload = []

				try:
					async for user in client.iter_participants(my_channel):
						users.append(user)
				except Exception as eee:
					print("unable to get users for ", normGid, eee)

				total = 0

				try:
					async with client.takeout() as takeout:
						print("New Takeout session Created: ", normGid)
						async for message in takeout.iter_messages(my_channel,wait_time=0):
							if message.id > total:
								total = message.id
							if len(messages) % 100 == 0:
								print(normGid, str(len(messages)) + "/" + str(total), "(" + str(message.id) + ")")
							messages.append(message.to_dict())
							
							if(message.media):
								messagesToDownload.append({
									"id": message.id,
									"media": message.media
								})
				except errors.TakeoutInitDelayError as e:
					print('Must wait', e.seconds, 'before takeout')
				except Exception as ge:
					print(ge)
					print("FAILED TO FULLY GET", normGid, "Last known id: ", messages[len(messages)-1].id)

				print(len(messages))
				# print(messages[0].stringify())

				with open('groups/' + normGid + '.json', 'w') as outfile:
					outfile.write(jsonpickle.encode(my_channel))
					print("saved group: ", normGid)
					

				with open('users/' + normGid + '.json', 'w') as outfile:
					outfile.write(jsonpickle.encode(users))
					print("saved users, count: " + str(len(users)))

				with open('messages/' + normGid + '.json', 'w') as outfile:
					# json_str = jsonpickle.encode(messages, unpicklable=True)
					print("saved messages, count: " + str(len(messages)))
					outfile.write(json.dumps(messages,cls=DateTimeEncoder))
					# outfile.write(json_str)
					print("saved string to disk")

				with open("mtd/"+ normGid + ".obj", 'w') as outfile:
					json_str = jsonpickle.encode(messagesToDownload)
					print("saved media messages, count: " + str(len(messagesToDownload)))
					outfile.write(json_str)
					print("saved to disk")
				


				# with open("mtd/"+ group_id.replace("https://t.me/", "").replace("\n","") + ".obj", 'r') as inFile:
				# 	json_str = inFile.read()
				# 	data = jsonpickle.decode(json_str)
				# 	# print(data)
				# 	for media in data:
				# 		await client.download_media(media["media"], "media/" + str(media["id"]))




			except Exception as inErr:
				exc_type, exc_value, exc_traceback = sys.exc_info()

				traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stdout)

		except Exception as err:
			print(err)


with client:
	client.loop.run_until_complete(main())
