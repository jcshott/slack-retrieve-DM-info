import requests, datetime, time, sys, os, argparse, ConfigParser

def set_up():
	"""
	You can pass in an output file handle for message text; config file to read from (required); 
	timestamp from which to read forward and a log file to indicate last time that was read (so as to only capture new meessages when running program)
	"""
	set_up_info = {}

	parser = argparse.ArgumentParser(description="Retrieve DM info from Slack")
	parser.add_argument('-o', '--output', action='store', dest="output_file", help='define output_file')
	parser.add_argument('-t', '--timestamp', action='store', dest='last_timestamp', help="define timestamp from which start download (exclusive), if known")
	parser.add_argument('-c', '--config', action='store', dest='config_file_handle', help='indicate config file handle to read from for settings', required=True)
	parser.add_argument('-l', '--log', action='store', dest='log_file_handle', help='indicate log file handle that will store timestamp of the last message read after running program')
	parse_results = parser.parse_args()

	#open and read the config file - handle must be passed in thru cmd line -c or --config. 
	config_handle = parse_results.config_file_handle
	config = ConfigParser.ConfigParser()
	config.read(config_handle)

	### OUTPUT FILE SPECIFICATIONS ###
	if parse_results.output_file: #check if user gave output file on cmd line
		output_file = parse_results.output_file
		set_up_info['output_file'] = output_file
	else:
		try:
			output_file = config.get('SlackParams', 'output_file') #look in config file, if not there, create an output file
			set_up_info['output_file'] = output_file
		except ConfigParser.NoOptionError:
			output_file = "output.txt"
			set_up_info['output_file'] = output_file
	
	### TIMESTAMP FROM WHICH TO READ MESSAGES AFTER SPECIFICATION ###
	if parse_results.last_timestamp: #if timestamp given on cmd line, use that
		start_timestamp = parse_results.last_timestamp
		set_up_info['start_timestamp'] = start_timestamp
	elif parse_results.log_file_handle: #if given log filehandle on cmd line, read from that
		log_handle = parse_results.log_file_handle
		with open(log_handle, 'a+') as log: #opens file for appending and reading, creates file if doesn't exist
			log_data = log.readlines()
			if not log_data: #if you don't have any timestamp data, set to 0 to get all history
				start_timestamp = 0
				set_up_info['start_timestamp'] = start_timestamp
			else:
				start_timestamp = log_data[-1]
				set_up_info['start_timestamp'] = start_timestamp
		log.closed
	else:
		try:
			log_handle = config.get('SlackParams', 'log_file') #try to get log file handle from config.
			with open(log_handle, 'a+') as log:
				log_data = log.readlines()
				if not log_data: #if you don't have any timestamp data, set to 0 to get all history
					start_timestamp = 0
					set_up_info['start_timestamp'] = start_timestamp
				else:
					start_timestamp = log_data[-1]
					set_up_info['start_timestamp'] = start_timestamp
			log.closed
		except ConfigParser.NoOptionError:
			start_timestamp = 0 #if neither cmd line or log file given, all messages will be downloaded
			set_up_info['start_timestamp'] = start_timestamp
	

	### TIMESTAMP LOG FILE SPECIFICATIONS ###
	if parse_results.log_file_handle:
		log_file = parse_results.log_file_handle #read in the given log file from cmd line
		set_up_info['log_file'] = log_file
	else:
		try:
			log_file = config.get('SlackParams', 'log_file') #if not on cmd line -> check the config file
			set_up_info['log_file'] = log_file
		except ConfigParser.NoOptionError:
			log_file = "log.txt" #if none given, create log.txt to store timestamps
			set_up_info['log_file'] = log_file
	
	### SPECS THAT MUST BE SET IN CONFIG FILE ###
	mytoken = config.get('SlackParams', 'slack_token')
	set_up_info['mytoken'] = mytoken
	channel = config.get('SlackParams', 'channel')
	set_up_info['channel'] = channel

	return set_up_info

def get_dm_info():
	"""appends to specified output_file the messages in a specified DM channel in the following format:
	MM-DD-YY, time of message: user name of sender - message text

	necessary variables are set via config file or from command line - including: output file handle; DM channel to download; last timestamp from which to read forward (not including message at that timestamp); log file handle to record timestamp from last time program was run (so you can run program and only get new messages); Slack API Token (REQUIRED to be in config file)
	"""
	var_info = set_up()

	output_file = var_info['output_file']
	log_file = var_info['log_file']
	start_timestamp = var_info['start_timestamp']
	mytoken = var_info['mytoken']
	channel = var_info['channel']

	with open(output_file, 'a') as f:
		with open(log_file, 'a') as l:
			#account for more than default 100 mgs retrieval. if api call returns that there are no more msgs. this becomes False and loop breaks
			run = True 
			
			while run:
				query_params = {'token': mytoken,
								'channel': channel,
								'oldest': str(start_timestamp)
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
						user_name = get_user_name(user_id, mytoken)
						users_seen[user_id] = user_name

					day_sent = datetime.datetime.fromtimestamp(float(msg["ts"]))
				
					msgs.append([day_sent.strftime("%a. %m-%d-%Y, %I:%M %p"), user_name, msg["text"]])
					
					if msg["ts"] > latest_timestamp:
						latest_timestamp = msg["ts"]

				sorted_msgs = sorted(msgs) #msgs are returned in JSON, unsorted, so sort by date/time for output

				for x in sorted_msgs:
					f.write(x[0].encode("utf-8") + ": " + x[1].encode("utf-8") + " - " + x[2].encode("utf-8") + "\n")

				l.write(str(latest_timestamp) + '\n')

				if not response["has_more"]:
					run = False
				else:
					start_timestamp = latest_timestamp

		l.close()
	f.close()

def get_user_name(user_id, mytoken):
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

	get_dm_info()
