#!/usr/bin/env python
# BadParent
# Developed by acidvegas in Python
# https://github.com/acidvegas/trollbots
# config.py

class connection:
	server  = 'irc.server.com'
	port    = 6667
	proxy   = None # Proxy should be a Socks 5 in IP:PORT format.
	ipv6    = False
	ssl     = False
	vhost   = None
	channel = '#chat'
	key     = None

class cert:
	key      = None
	file     = None
	password = None

class ident:
	nickname = 'BadParent'
	username = 'badparent'
	realname = 'BadParent IRC Bot'

class login:
	network  = None
	nickserv = None

class throttle
	concurrency = 3
	pm          = 1.5
	threads     = 100
	timeout     = 15

class settings:
	msg = 'I was raised by bad parents so I flood on IRC...'