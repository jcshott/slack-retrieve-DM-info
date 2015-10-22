import requests, datetime, time, sys, os
#make the timestamps go into a log file and then have the program read the last entry to get next block of messages to download. if nothing in log file, then have it default to getting all history
mytoken = os.environ.get("SLACK_TOKEN")
	
def get_dm_info(outputfile):
	
	with open(outputfile, 'a') as f:

		query_params = {'token': mytoken,
						'channel': "D076VAAKY",
						# 'oldest': str(last_import_ts)
					       }
		endpoint = 'https://slack.com/api/im.history'
		response = requests.get(endpoint, params=query_params).json()

		msgs = []
		latest_timestamp = 0

		for msg in response["messages"]:
			user_id = msg["user"]
			user_name = get_user_name(user_id)
			day_sent = datetime.datetime.fromtimestamp(float(msg["ts"]))
		
			msgs.append([day_sent.strftime("%a. %m-%d-%Y, %I:%M %p"), user_name, msg["text"]])
			
			if msg["ts"] > latest_timestamp:
				latest_timestamp = msg["ts"]

		sorted_msgs = sorted(msgs)

		for x in sorted_msgs:
			f.write(x[0].encode("utf-8") + ": " + x[1].encode("utf-8") + " - " + x[2].encode("utf-8") + "\n")

		f.write("last timestmp: %r" % latest_timestamp)
		latest_date = datetime.datetime.fromtimestamp(float(latest_timestamp))
		f.write(latest_date.strftime("%m-%d-%Y"))
	
	f.close()

def get_user_name(user_id):
	"""Makes Slack API call to get name of a user with a given ID

	takes in a Slack user ID as string, returns real_name. if no real_name is found in profile, returns "name" field"""

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
		return "no user with ID"

if __name__ == '__main__':
	# try:
	# 	last_import_ts = sys.argv[1]
	# 	outputfile = sys.argv[2]	
	# except IndexError:
	# 	print "Try again. Please provide the last timestamp for which you want to pull message data as the 2nd command line argument and output filename for the third"
	
	get_dm_info('test.txt')
	