#!/usr/bin/env python
# EFknockr (EFK)
# Developed by acidvegas in Python
# https://github.com/acidvegas/trollbots
# efknockr.py

import concurrent.futures
import os
import random
import socket
import ssl
import sys
import threading
import time

sys.dont_write_bytecode = True

import config

# Bad IRC Events
bad_msgs = (
	'Color is not permitted',
	'No external channel messages',
	'You need voice',
	'You must have a registered nick'
)

bad_numerics = {
	'471' : 'ERR_CHANNELISFULL',
	'473' : 'ERR_INVITEONLYCHAN',
	'474' : 'ERR_BANNEDFROMCHAN',
	'475' : 'ERR_BADCHANNELKEY',
	'477' : 'ERR_NEEDREGGEDNICK',
	'489' : 'ERR_SECUREONLYCHAN',
	'519' : 'ERR_TOOMANYUSERS',
	'520' : 'ERR_OPERONLY'
}

def debug(msg):
	print(f'{get_time()} | [~] - {msg}')

def error(msg, reason=None):
	if reason:
		print(f'{get_time()} | [!] - {msg} ({reason})')
	else:
		print(f'{get_time()} | [!] - {msg}')

def error_exit(msg):
	raise SystemExit(f'{get_time()} | [!] - {msg}')

def get_time():
	return time.strftime('%I:%M:%S')

class clone:
	def __init__(self, server, options):
		self.server           = server
		self.options          = options
		self.bad_channels     = list()
		self.current_channels = list()
		self.nicklist         = dict()
		self.nickname         = None
		self.sock             = None

	def run(self):
		if not self.options:
			self.options = config.defaults
		else:
			self.options.update(config.defaults)
		self.nickname = self.options['nickname']
		self.connect()

	def attack(self):
		while self.options['channels']:
			chan = random.choice(self.options['channels'])
			try:
				self.join_channel(chan)
			except Exception as ex:
				error('Error occured in the attack loop!', ex)
				break
			else:
				time.sleep(config.throttle.join)
				while len(self.current_channels) >= config.throttle.channels:
					time.sleep(1)
			finally:
				self.options['channels'].remove(chan)
		debug('Finished knocking all channels on ' + self.server)
		self.event_disconnect()

	def connect(self):
		try:
			self.create_socket()
			self.sock.connect((self.server, self.options['port']))
			self.register()
		except socket.error:
			error('Failed to connect to ' + self.server)
			self.event_disconnect()
		else:
			self.listen()

	def create_socket(self):
		family = socket.AF_INET6 if self.options['ipv6'] else socket.AF_INET
		if config.connection.proxy:
			proxy_server, proxy_port = config.settings.proxy.split(':')
			self.sock = socks.socksocket(family, socket.SOCK_STREAM)
			self.sock.setblocking(0)
			self.sock.setproxy(socks.PROXY_TYPE_SOCKS5, proxy_server, int(proxy_port))
		else:
			self.sock = socket.socket(family, socket.SOCK_STREAM)
		self.sock.settimeout(config.throttle.timeout)
		if config.connection.vhost:
			self.sock.bind((config.connection.vhost, 0))
		if self.options['ssl']:
			self.sock = ssl.wrap_socket(self.sock)

	def event_connect(self):
		debug('Connected to ' + self.server)
		if self.options['nickserv']:
			self.identify(self.options['nickname'], self.options['nickserv'])
		if self.options['channels']:
			if type(self.options['channels']) == list:
 				threading.Thread(target=self.attack).start()
			else:
				error('Invalid channel list for ' + self.server)
				self.event_disconnect()
		else:
			self.options['channels'] = list()
			self.raw('LIST >' + str(config.throttle.users))

	def event_disconnect(self):
		self.sock.close()

	def event_end_of_list(self):
		if self.options['channels']:
			debug('Found {0} channels on {1}'.format(len(self.options['channels']), self.server))
			threading.Thread(target=self.attack).start()
		else:
			error('Found zero channels on ' + self.server)
			self.event_disconnect()

	def event_end_of_names(self, chan):
		self.current_channels.append(chan)
		debug(f'Knocking {chan} channel on {self.server}...')
		try:
			for line in msg_lines:
				if chan in self.bad_channels:
					break
				self.sendmsg(chan, line)
				time.sleep(config.throttle.message)
			if chan in self.nicklist:
				self.nicklist[chan] = ' '.join(self.nicklist[chan])
				if len(self.nicklist[chan]) <= 400:
					self.sendmsg(chan, self.nicklist[chan])
				else:
					while len(self.nicklist[chan]) > 400:
						if chan in self.bad_channels:
							break
						segment = self.nicklist[chan][:400]
						segment = segment[:-len(segment.split()[len(segment.split())-1])]
						self.sendmsg(chan, segment)
						self.nicklist[chan] = self.nicklist[chan][len(segment):]
						time.sleep(config.throttle.message)
			self.part(chan, config.settings.part_msg)
		except Exception as ex:
			error('Error occured in the attack loop!', ex)
		finally:
			self.current_channels.remove(chan)
			if chan in self.bad_channels:
				self.bad_channels.remove(chan)
			if chan in self.nicklist:
				del self.nicklist[chan]

	def event_list_channel(self, chan, users):
		self.options['channels'].append(chan)

	def event_nick_in_use(self):
		self.nickname += '_'
		self.nick(self.nickname)

	def event_names(self, chan, names):
		if config.settings.mass_hilite:
			if chan not in self.nicklist:
				self.nicklist[chan] = list()
			for name in names:
				if name[:1] in '~!@%&+:':
					name = name[1:]
				if name != self.nickname and name not in self.nicklist[chan]:
					self.nicklist[chan].append(name)

	def handle_events(self, data):
		args = data.split()
		if data.startswith('ERROR :Closing Link:'):
			if 'Password mismatch' in data:
				error('Network has a password.', self.server)
			raise Exception('Connection has closed.')
		elif args[0] == 'PING':
			self.raw('PONG ' + args[1][1:])
		elif args[1] == '001':
			self.event_connect()
		elif args[1] == '322':
			if len(args) >= 5:
				chan  = args[3]
				users = args[4]
				self.event_list_channel(chan, users)
		elif args[1] == '323':
			self.event_end_of_list()
		elif args[1] == '353':
			chan = args[4]
			if chan + ' :' in data:
				names = data.split(chan + ' :')[1].split()
			elif ' *' in data:
				names = data.split(' *')[1].split()
			elif ' =' in data:
				names = data.split(' =')[1].split()
			else:
				names = data.split(chan)[1].split()
			self.event_names(chan, names)
		elif args[1] == '366':
			chan = args[3]
			threading.Thread(target=self.event_end_of_names, args=(chan,)).start()
		elif args[1] == '404':
			chan = args[3]
			for item in bad_msgs:
				if item in data:
					error(f'Failed to message {chan} channel on {self.server}', '404: ' + item)
					if chan not in self.bad_channels:
						self.bad_channels.append(chan)
						break
		elif args[1] == '433':
			self.event_nick_in_use()
		elif args[1] == '464':
			error('Network has a password.', self.server)
		elif args[1] in bad_numerics:
			chan = args[3]
			error(f'Failed to knock {chan} channel on {self.server}', bad_numerics[args[1]])

	def identify(nick, password):
		self.sendmsg('nickserv', f'identify {nick} {password}')

	def join_channel(self, chan):
		self.raw('JOIN ' + chan)

	def listen(self):
		while True:
			try:
				data = self.sock.recv(1024).decode('utf-8')
				for line in (line for line in data.split('\r\n') if line):
					if len(line.split()) >= 2:
						self.handle_events(line)
			except (UnicodeDecodeError,UnicodeEncodeError):
				pass
			except Exception as ex:
				error('Unexpected error occured.', ex)
				break
		self.event_disconnect()

	def nick(self, nick):
		self.raw('NICK ' + nick)

	def part(self, chan, msg):
		self.raw(f'PART {chan} :{msg}')

	def raw(self, msg):
		self.sock.send(bytes(msg + '\r\n', 'utf-8'))

	def register(self):
		if self.options['password']:
			self.raw('PASS ' + self.options['password'])
		self.raw('USER {0} 0 * :{1}'.format(self.options['username'], self.options['realname']))
		self.raw('NICK ' + self.nickname)

	def sendmsg(self, target, msg):
		self.raw(f'PRIVMSG {target} :{msg}')

# Main
print('#'*56)
print('#{0}#'.format(''.center(54)))
print('#{0}#'.format('EFknockr (EFK)'.center(54)))
print('#{0}#'.format('Developed by acidvegas in Python'.center(54)))
print('#{0}#'.format('https://github.com/acidvegas/trollbots'.center(54)))
print('#{0}#'.format(''.center(54)))
print('#'*56)
if config.connection.proxy:
	try:
		import socks
	except ImportError:
		error_exit('Missing PySocks module! (https://pypi.python.org/pypi/PySocks)')
msg_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'msg.txt')
if os.path.isfile(msg_file):
	msg_lines = (line.strip() for line in open(msg_file, encoding='utf8', errors='replace').readlines() if line)
else:
	error_exit('Missing message file!')
del msg_file
debug(f'Loaded {len(config.targets)} targets from config.')
server_list = list(config.targets)
random.shuffle(server_list)
with concurrent.futures.ThreadPoolExecutor(max_workers=config.throttle.threads) as executor:
	checks = {executor.submit(clone(server, config.targets[server]).run): server for server in server_list}
	for future in concurrent.futures.as_completed(checks):
		checks[future]
debug('EFknockr has finished knocking.')