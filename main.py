#! /usr/bin/python
import urwid
import time
import platform
import psutil
import datetime

refresh_rate = 1

def exit_on_q(key):
	if key in ('q', 'Q'):
		raise urwid.ExitMainLoop()

def secToStr(sec):
	d = datetime.datetime(1, 1, 1) + datetime.timedelta(seconds=sec)

	return str(d.day - 1) + ' days, ' + str(d.hour) + ' hours, ' + str(d.minute) + ' minutes, ' + str(d.second) + ' seconds.'

def getProcesses():
	pinfo = []
	processcount = 0
	for proc in psutil.process_iter():
		try:
			pinfo.append(proc.as_dict(attrs=['pid', 'name', 'cpu_percent']))
			processcount += 1
		except psutil.NoSuchProcess:
			pass

	procs = sorted(pinfo, key = lambda proc: 100 - proc['cpu_percent'])
	procstr = ''

	for proc in procs:
		procstr += str(proc['cpu_percent']) + '% ' + proc['name'] + '\n'

	return (processcount, procstr)



def updateScreen(loop, data):
	t = datetime.datetime.now()
	bannertxt.set_text(('green', platform.node() + ' ' + t.strftime('%m/%d/%Y %H:%M:%S')))

	cpubar.set_completion(psutil.cpu_percent())

	mem = psutil.virtual_memory()
	meminfo.set_text('Total: ' + str(mem.total / 1024 ** 2) + 'MB, Available: ' + str(mem.available / 1024 ** 2) + 'MB')
	membar.set_completion(mem.percent)

	swap = psutil.swap_memory()
	swapinfo.set_text('Total: ' + str(swap.total / 1024 ** 2) + 'MB, Free: ' + str(swap.free / 1024 ** 2) + 'MB')
	swapbar.set_completion(swap.percent)

	users = psutil.users()
	usersstr = ''
	usercount = 0
	for user in users:
		usersstr = usersstr + user.name + '@' + user.host + ' on ' + user.terminal + ' logged in on ' + str(datetime.datetime.fromtimestamp(user.started).strftime("%Y-%m-%d at %H:%M:%S") + '\n\n')
		usercount += 1

	userstitle.set_text(('title', 'Logged in users (' + str(usercount) + ')'))
	userstxt.set_text(usersstr[:-2])

	boot = datetime.datetime.fromtimestamp(psutil.boot_time())
	uptime = datetime.datetime.now() - boot
	uptime = secToStr(uptime.seconds)
	uptimetxt.set_text(uptime)

	(pcount, pinfo) = getProcesses()
	processtitle.set_text(('title', 'Running Processes(' + str(pcount) + ')'))
	processtxt.set_text(pinfo)

	loop.set_alarm_in(refresh_rate, updateScreen)

palette = [
		('bg', 'white', 'black'),
		('streak', 'dark green, bold', 'black'),
		('title', 'dark green, bold', 'black'),
		('green', 'black', 'dark green'),
		('divider', 'dark blue', 'black'),
		('gray', 'black', 'light gray')
		]

bannertxt = urwid.Text(('green', platform.node()), align='center')
banner = urwid.Filler(bannertxt, valign='top', height='pack')
banner = urwid.AttrMap(banner, 'streak')

divider = urwid.Divider(u'-')
divider = urwid.AttrMap(divider, 'divider')
divider2 = urwid.Divider(' ')

cputxt = urwid.Text(('title', 'CPU Usage'))
cpuinfo = urwid.Text('Cores: ' + str(psutil.cpu_count()) + ', CPUs: ' + str(psutil.cpu_count(logical=False)))
cpubar = urwid.ProgressBar('gray', 'green', psutil.cpu_percent(), 100)

memtxt = urwid.Text(('title', 'Mem Usage'))
mem = psutil.virtual_memory()
meminfo = urwid.Text('Total: ' + str(mem.total / 1024 ** 2) + 'MB, Available: ' + str(mem.available / 1024 ** 2) + 'MB')
membar = urwid.ProgressBar('gray', 'green', mem.percent)

swaptxt = urwid.Text(('title', 'Swap Usage'))
swap = psutil.swap_memory()
swapinfo = urwid.Text('Total: ' + str(swap.total / 1024 ** 2) + 'MB, Free: ' + str(swap.free / 1024 ** 2) + 'MB')
swapbar = urwid.ProgressBar('gray', 'green', swap.percent)

disktxt = urwid.Text(('title', 'Disk Usage'))

diskmain = psutil.disk_usage('/')
diskmaintxt = urwid.Text('/')
diskmainbar = urwid.ProgressBar('gray', 'green', diskmain.percent)
diskmaininfo = urwid.Text('Total: ' + str(diskmain.total / 1024 ** 3) + 'GB, Free: ' + str(diskmain.free / 1024 ** 3) + 'GB')

diskhome = psutil.disk_usage('/home')
diskhometxt = urwid.Text('/home')
diskhomebar = urwid.ProgressBar('gray', 'green', diskhome.percent)
diskhomeinfo = urwid.Text('Total: ' + str(diskhome.total / 1024 ** 3) + 'GB, Free: ' + str(diskhome.free / 1024 ** 3) + 'GB')

uptimetitle = urwid.Text(('title', 'Uptime'))
boot = datetime.datetime.fromtimestamp(psutil.boot_time())
uptime = datetime.datetime.now() - boot
uptime = secToStr(uptime.seconds)
uptimetxt = urwid.Text(uptime)

userstitle = urwid.Text(('title', 'Logged in users'))
usersstr = ''
userstxt = urwid.Text(usersstr)

processtitle = urwid.Text(('title', 'Running Processes'))
(pcount, pinfo) = getProcesses()
processtxt = urwid.Text(pinfo)

frame1 = urwid.ListBox(
		[
			cputxt, cpubar, cpuinfo, divider,
			memtxt, membar, meminfo, divider,
			swaptxt, swapbar, swapinfo, divider,
			disktxt, diskmaintxt, diskmainbar, diskmaininfo,
			divider2, diskhometxt, diskhomebar, diskhomeinfo,
		])

frame1 = urwid.AttrMap(frame1, 'bg')

frame2 = urwid.ListBox(
		[
			uptimetitle, uptimetxt, divider,
			userstitle, userstxt, divider
		])
frame2 = urwid.AttrMap(frame2, 'bg')
frame2 = urwid.Padding(frame2, left=1)

frame3 = urwid.ListBox([processtitle, processtxt])
frame3 = urwid.AttrMap(frame3, 'bg')
frame3 = urwid.Padding(frame3, left=1)

columns = urwid.Columns([frame1, frame2, frame3])
columns = urwid.AttrMap(columns, 'bg')

topwidget = urwid.Pile([(1, banner), columns])



loop = urwid.MainLoop(topwidget, palette, unhandled_input=exit_on_q)
loop.set_alarm_in(0, updateScreen)
loop.run()
