import requests, datetime, time, sys, os, argparse
#make the timestamps go into a log file and then have the program read the last entry to get next block of messages to download. if nothing in log file, then have it default to getting all history

def get_dm_info(output_file, start_timestamp=0):
	"""appends to specified output_file the messages in a DM channel.
	takes in output_file name and beginning timestamp. returns nothing, 
	appends to specified file the following info: 
	MM-DD-YY, time of message: user_name of sender - message text
	"""

	with open(output_file, 'a') as f:

		query_params = {'token': mytoken,
						'channel': "D076VAAKY",
						# 'oldest': str(start_timestamp)
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

	parser = argparse.ArgumentParser(description="Retrieve DM info from Slack")
	parser.parse_args()
	parser.add_argument('-o', '--o', action='store_const', dest='output_file', help='define output_file')
	# if len(sys.argv) == 2:
	# 	try:
	# 		output_file = sys.argv[1]
	# 		start_timestamp = sys.argv[2]	
	# 	except:
	# 		print "If you are providing both a starting timestamp and output file name, please provide the filename first and timestamp second"
	mytoken = os.environ.get("SLACK_TOKEN")
	get_dm_info('test.txt')

	#if timestamp parameter given - use that (argparse library)
	#if not - check if there's a log file and read last line (in a function above)
	#if no log file or parameter given, get everything

	#config file - put the channel, api key, output file name
	#http://stackoverflow.com/questions/8225954/python-configuration-file-any-file-format-recommendation-ini-format-still-appr
	