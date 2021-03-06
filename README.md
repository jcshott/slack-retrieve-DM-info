Slack - Direct Message Retrieval
====================================
Python script to utilize Slack's API to retrieve your direct message history with a user and output the conversation to a txt file in the following format:

DAY DATE, TIME: User_name - Message text

Example:

>Wed. 10-21-2015, 12:55 PM: Corey Shott - Thanks for the great suggestion. Isn't coding fun?!?

>Wed. 10-21-2015, 12:57 PM: Joe Schmo - You are welcome. Yes! :simple_smile:

This program is configured to keep track of the timestamp of the last message retrieved so if you run this on a regular basis, you can retrieve only new messages and have them appended to the same file.

____

## Required Info ##

* <b> Python 2.7.1</b>
* <b> [requests](https://pypi.org/project/requests/) </b>

* <b>Slack API Token</b>:  Obtain a token from [Slack's API Site](https://api.slack.com/apps).
	+ You'll need to create a new App and add it to your Workspace.
	+ Under "Add features and functionality" -> "Permissions" -> "Scopes": Give the app permission to Access the following:
	```
	Access user’s public channels
	channels:history

	Access information about user’s public channels
	channels:read

	Access content in user’s private channels
	groups:history

	Access your workspace’s profile information
	users:read
	```
	+ make sure you do the Install your app in your workspace step (under Basic Information)
	+ use `OAuth Access Token` (found in `OAuth & Permissions` section where you set up Scope) as your `slack_token` in config
* <b>Channel ID:</b> Identify the Channel Id (ex. D1234567890) for which you want to use this program.

####Getting Channel ID

I haven't found an elegant solution to finding the channel ID.  Here's how I did it, would appreciate feedback if you know a better way:

1. Sign-in to your Slack Workspace in a web browser (ex. WORKSPACE.slack.com)
2. Find channel you want to retrieve history
3. A new page will open.  In the web address will be a url, you want the last part. If the url is:
```
https://app.slack.com/client/T2VU4K6EA/CF35KMD9Q
```
you want to use `CF35KMD9Q` as the channel

____

## Set-Up ##

**Create Config File**
This should store the information needed for the program to call the API and output correct information to a file.  Format the file as follows:

<kbd>config.ini</kbd>

```
[SlackParams]
channel = DXXXXXX (channel id)
slack_token = YOUR TOKEN HERE
log_file = FILE NAME OF WHERE YOU WANT TIMESTAMP INFO LOGGED (i.e. log.txt)
output_file = FILE NAME OF WHERE YOU WANT MESSAGE INFO RECORDED (i.e. output.txt)
```
The only *required* information in the config file is the **channel** and the **slack_token**.  The other items can be handled on command line or, if not given in either location, default <kbd>log.txt</kbd> and <kbd>output.txt</kbd> files will be created in first run of program.

## Running Program ##

In directory for the project:

```sh
$ git clone https://github.com/jcshott/slack-retrieve-DM-info.git
```

If you have set up the <kbd>config.ini</kbd> file as outlined above, you can just run the program, specifying config file name on command line as such:

```sh
$ python slack_channel_history_retrieve.py -c config.ini (or whatever name you gave it, as long as its a *.ini file) `
```

If you did not set a log file name and/or output file name in the config file. you can do so with the following command line arguments:

####Output filename specification

```sh
$ python slack_channel_history_retrieve.py -c config.ini -o output.txt
```

####Log filename specification

```sh
$ python slack_channel_history_retrieve.py -c config.ini -l log.txt
```

The log file will capture the last timestamp of the last message downloaded and outputted to file.  If you plan to run the file more than once (like 1x/day or week), the program will read the last timestamp logged in the log file and only retrieve messages after that timestamp.  Thus, it is in your best interest to keep the log file the same name after creation - either by specifying it in config file, on command line or keeping it the default.


Similarly, the output from retrieval will got to specified output file and will append each run, the new messages - if you keep that file name the same.

Lastly, the timestamp from which you want to retrieve messages after can be specified on the command line as well, though it is suggested to utilize the log file function instead for ongoing runs of the program so as to avoid duplication of message retrieval.

####Timestamp specification example

```sh
$ python slack_channel_history_retrieve.py -c config.ini -t 1445457322.000006
```

<b>Note:</b> For the optional command line arguments, if you specify via command line, those specs will override specs in your config file.

By default, the API response only returns the first 200 messages, along with a boolean value of "has_more".  If that is set to "true", retrieval script will run, with updated starting timestamp, until all messages are retrieved and "has_more" returns False.
