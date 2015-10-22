import requests, datetime, time, sys, os
#make the timestamps go into a log file and then have the program read the last entry to get next block of messages to download. if nothing in log file, then have it default to getting all history

def get_dm_info(outputfile):
	"""appends to specified outputfile the messages in a DM channel.
	takes in outputfile name and beginning timestamp. returns nothing, 
	appends to specified file the following info: 
	MM-DD-YY, time of message: user_name of sender - message text
	"""

	with open(outputfile, 'a') as f:

		query_params = {'token': mytoken,
						'channel': "D076VAAKY",
						# 'oldest': str(last_import_ts)
					       }
		endpoint = 'https://slack.com/api/im.history'
		response = requests.get(endpoint, params=query_params).json()

		users_seen = {}
		msgs = []
		latest_timestamp = 0

		for msg in response["messages"]:
			user_id = msg["user"]
			if user_id in users_seen:
				user_name = users_seen.get(user_id)
			else:
				user_name = get_user_name(user_id)
				users_seen[user_id] = user_name

			day_sent = datetime.datetime.fromtimestamp(float(msg["ts"]))
		
			msgs.append([day_sent.strftime("%a. %m-%d-%Y, %I:%M %p"), user_name, msg["text"]])
			
			if msg["ts"] > latest_timestamp:
				latest_timestamp = msg["ts"]
		print "users_seen: ", user_dict
		sorted_msgs = sorted(msgs)

		for x in sorted_msgs:
			f.write(x[0].encode("utf-8") + ": " + x[1].encode("utf-8") + " - " + x[2].encode("utf-8") + "\n")

		f.write("last timestmp: %r" % latest_timestamp)
	
	f.close()

def get_user_name(user_id):
	"""Makes Slack API call to get name of a user with a given ID

	takes in a Slack user ID as string, returns real_name. if no real_name is found in profile, returns "name" field. if no user found, return None"""

	query_params = {'token': mytoken,
					'user': user_id
					}
	endpoint = 'https://slack.com/api/users.info'
	response = requests.get(endpoint, params=query_params).json()

	if response["ok"]:
		try:
		 	return response["user"]["profile"]["real_name"]
		except IndexError:
			return response["user"]["name"]
	else:
		return None

if __name__ == '__main__':
	# try:
	# 	last_import_ts = sys.argv[1]
	# 	outputfile = sys.argv[2]	
	# except IndexError:
	# 	print "Try again. Please provide the last timestamp for which you want to pull message data as the 2nd command line argument and output filename for the third"
	mytoken = os.environ.get("SLACK_TOKEN")
	get_dm_info('test.txt')
	