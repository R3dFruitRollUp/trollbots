#!/usr/bin/env python
# EFknockr (EFK)
# Developed by acidvegas in Python
# https://github.com/acidvegas/trollbots
# config.py

class connection:
	proxy = None # Proxy should be a Socks5 in IP:PORT format.
	vhost = None

class settings:
	mass_hilite = True # Hilite all the users in a channel before parting.
	part_msg    = 'Smell ya l8r'

class throttle:
	join     = 3   # Delay between each channel join.
	channels = 3   # Maximum number of channels to be flooding at once.
	threads  = 100 # Maximum number of threads running.
	users    = 10  # Minimum number of users required in a channel.
	message  = 0.5 # Delay between each message sent to a channel.
	timeout  = 10  # Timeout for all sockets.

# Attack List / Options
defaults = {
	'port'     : 6667,
	'ipv6'     : False,
	'ssl'      : False,
	'password' : None, # This is the network password issued on connect.
	'channels' : None, # Setting channels to None will crawl all channels.
	'nickname' : 'EFknockr',
	'username' : 'efk',
	'realname' : 'EFknockr IRC Bot',
	'nickserv' : None
}

targets  = {
	'irc.server1.com' : None,                                              # None as the server options will use the default settings.
	'irc.server2.com' : {'port':6697, 'ssl':True},                         # Change the default settings by specifying options to change.
	'irc.server3.com' : {'channels':['#channel1','#channel2','#channel3']} # Setting specific channels can be done with a list.
}