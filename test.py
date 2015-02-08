#! /usr/bin/python
import psutil

pinfo = []
for proc in psutil.process_iter():
	try:
		pinfo.append(proc.as_dict(attrs=['pid', 'name']))
	except psutil.NoSuchProcess:
		pass

print(sorted(pinfo, key = lambda proc: proc['name']))
