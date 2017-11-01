#!/usr/bin/env python
# Jupiter
# Developed by acidvegas in Python
# https://github.com/acidvegas/trollbots
# jupiter.py

import random
import socket
import string
import time

# Connection
server     = 'irc.server.com'
port       = 6667
proxy      = None # Proxy should be a Socks5 in IP:PORT format.
use_ipv6   = False
use_ssl    = False
vhost      = None
channel    = '#jupiter'
key        = None

# Identity
nickname = 'Jupiter'
username = 'jupiter'
realname = 'https://github.com/acidvegas/trollbots'

# Settings
admin_ident = 'user@host.name'
user_modes  = None

# Throttle
ison_delay = 3
reconnect  = 10
rejoin     = 3

# Formatting Control Characters / Color Codes
bold        = '\x02'
italic      = '\x1D'
underline   = '\x1F'
reverse     = '\x16'
reset       = '\x0f'
white       = '00'
black       = '01'
blue        = '02'
green       = '03'
red         = '04'
brown       = '05'
purple      = '06'
orange      = '07'
yellow      = '08'
light_green = '09'
cyan        = '10'
light_cyan  = '11'
light_blue  = '12'
pink        = '13'
grey        = '14'
light_grey  = '15'

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

def random_str(size):
    return ''.join(random.choice(string.ascii_letters) for _ in range(size))

class Jupiter(object):
	def __init__(self):
		self.monlist  = list()
		self.nickname = nickname
		self.sock     = None
		self.use_ison = False

	def action(self, target, msg):
		self.sendmsg(target, f'\x01ACTION {msg}\x01')

	def color(self, msg, foreground, background=None):
		if background:
			return f'\x03{foreground},{background}{msg}{reset}'
		else:
			return f'\x03{foreground}{msg}{reset}'

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
		if vhost:
			self.sock.bind((vhost, 0))
		if use_ssl:
			ctx = ssl.SSLContext()
			if cert_file:
				ctx.load_cert_chain(cert_file, cert_key, cert_pass)
				ctx.check_hostname = False
				ctx.verify_mode = ssl.CERT_NONE
			self.sock = ctx.wrap_socket(self.sock)

	def error(self, target, data, reason=None):
		if reason:
			self.sendmsg(target, '[{0}] {1} {2}'.format(self.color('!', red), data, self.color('({0})'.format(reason), grey)))
		else:
			self.sendmsg(target, '[{0}] {1}'.format(self.color('!', red), data))

	def event_connect(self):
		if user_modes:
			self.mode(nickname, '+' + user_modes)
		if self.monlist:
			self.monitor('+', self.monlist)
		self.join_channel(channel, key)

	def event_disconnect(self):
		self.sock.close()
		time.sleep(reconnect)
		self.connect()

	def event_ison_reply(self, nicks):
		offline_nicks = [mon_nick for mon_nick in self.monlist if mon_nick not in nicks]:
		if offline_nicks:
			self.nick(random.choice(offline_nicks))

	def event_kick(self, nick, chan, kicked):
		if kicked == nickname and chan == channel:
			time.sleep(rejoin)
			self.join_channel(chan, key)

	def event_monitor_nick_offline(self, nick):
		self.nick(nick)

	def event_nick(self, new_nick):
		self.juped = True
		self.nickname = new_nick
		self.monlist.remove(new_nick)
		self.monitor('C')

	def event_nick_in_use(self, nick):
		error(nick + ' is in use.')
		if nick == self.nickname:
			self.nickname = random_str(8)
			self.nick(self.nickname)

	def event_private(self, nick, ident, msg):
		if ident == admin_ident:
			args = msg.split()
			if msg == '.monitor' and self.juped:
				self.juped = False
				if self.monlist:
					self.action('Monitoring list...')
					if self.use_ison:
						threading.Thread(target=self.loop).start()
					else:
						self.monitor('+', self.monlist)
			elif msg == '.monitor list':
				if self.monlist:
					self.sendmsg(nick, '[{0}]'.format(self.color('Monitor List', light_blue)))
					for mon_nick in self.monlist:
						self.sendmsg(nick, ' {0} {1}'.format(self.color('*', grey), mon_nick))
					self.sendmsg(nick, color(f'Total: {len(self.monlist)}', yellow))
				else:
					self.error(nick, 'Monitor list empty.')
			elif msg == '.monitor reset':
				if self.monlist:
					if not self.use_ison:
						self.monitor('C')
					self.sendmsg(nick, '{0} nick(s) have been {1} from the monitor list.'.format(self.color(len(self.monlist), cyan), self.color('removed', red)))
					self.monlist = list()
				else:
					self.error(nick, 'Monitor list already empty.')
			elif msg.startswith('.monitor + ') and len(args) == 3:
				nicks = [mon_nick for mon_nick in msg[11:].split() if mon_nick not in self.monlist]
				if nicks:
					self.monlist = self.monlist + nicks
					if not self.use_ison:
						self.monitor('+', nicks)
					self.sendmsg(nick, '{0} nick(s) have been {1} to the monitor list.'.format(self.color(len(nicks), cyan), self.color('added', green)))
				else:
					self.error(nick, 'No nicks added.')
			elif msg.startswith('.monitor - ') and len(args) == 3:
				nicks = [mon_nick for mon_nick in msg[11:].split() if mon_nick in self.monlist]
				if nicks:
					for mon_nick in nicks:
						self.monlist.remove(mon_nick)
					if not self.use_ison:
						self.monitor('-', nicks)
					self.sendmsg(nick, '{0} nick(s) have been {1} from the monitor list.'.format(self.color(len(nicks), cyan), self.color('removed', red)))
				else:
					self.error(nick, 'No nicks removed.')
			elif msg == '.status':
				if self.juped:
					self.sendmsg(nick, color('True', green))
				else:
					self.sendmsg(nick, color('False', red))
		else:
			self.sendmsg(channel, '[{0}] {1}{2}{3} {4}'.format(self.color('PM', red), self.color('<', grey), self.color(nick, yellow), self.color('>', grey), msg))

	def event_unknown_command(self):
		if not self.use_ison:
			import threading
			threading.Thread(target=self.loop).start()
			self.use_ison = True

	def handle_events(self, data):
		args = data.split()
		if data.startswith('ERROR :Closing Link:'):
			raise Exception('Connection has closed.')
		elif args[0] == 'PING':
			self.raw('PONG ' + args[1][1:])
		elif args[1] == '001':
			self.event_connect()
		elif args[1] == '303':
			nicks = data.split(f'args[0] 303 {args[1] :')[1].split()
			if nicks:
				self.event_ison_reply(nicks)
		elif args[1] == '421':
			self.event_unknown_command()
		elif args[1] == '433':
			nick = args[2]
			self.event_nick_in_use(nick)
		elif args[1] == '731':
			nick = args[3][1:]
			Events.monitor_nick_offline(nick)
		elif args[1] == 'NICK':
			nick = args[0].split('!')[0][1:]
			if nick == self.nickname:
				new_nick = args[2][1:]
				self.event_nick(nick)
		elif args[1] == 'PRIVMSG':
			target = args[2]
			if target == self.nickname:
				nick  = args[0].split('!')[0][1:]
				ident = args[0].split('!')[1]
				msg   = data.split(f'{args[0]} PRIVMSG {target} :')[1]
				self.event_private(nick, ident, msg)

	def ison(self, nicks):
		self.raw('ISON ' + ','.join(nicks))

	def join_channel(self, chan, key=None):
		if key:
			self.raw(f'JOIN {chan} {key}')
		else:
			self.raw('JOIN ' + chan)

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

	def loop(self):
		while True:
			if self.juped:
				break
			else:
				try:
					self.ison(self.monlist)
				except:
					pass
				time.sleep(ison_delay)

	def mode(self, target, mode):
		self.raw(f'MODE {target} {mode}')

	def monitor(self, action, nicks=None):
		if nicks:
			self.raw(f'MONITOR {action} ' + ','.join(nicks))
		else:
			self.raw('MONITOR ' + action)

	def nick(self, nick):
		self.raw('NICK ' + nick)

	def raw(self, msg):
		self.sock.send(bytes(msg + '\r\n', 'utf-8'))

	def register(self):
		self.raw(f'USER {username} 0 * :{realname}')
		self.nick(nickname)

	def sendmsg(self, target, msg):
		self.raw(f'PRIVMSG {target} :{msg}')

# Main
if proxy:
	try:
		import socks
	except ImportError:
		error_exit('Missing PySocks module! (https://pypi.python.org/pypi/PySocks)')
if use_ssl:
	import ssl
Jupiter().connect()