import subprocess
import re
import sqlite3
import os
import sys



# Input an ip to be scanned as a string.
#
# No output, calls parse().
# 
# Will create a directory inside the 'targets' 
# dir in the project directory and store
# the scan output into it in a file named
# 'scan.txt' 

def scan(ip):  
	if not os.path.exists('targets'):
		os.makedirs('targets')
	if not os.path.exists('targets/' + ip):
		os.makedirs('targets/' + ip)
	cmd = ['./nmap/nmap'] + ['-sV', '-Pn', ip]
	wincmd = ['./winmap/nmap'] + ['-sV', '-Pn', ip] 
	scan = open('./targets/' + ip + '/scan.txt', 'w+')

	with scan as outfile:
		if sys.platform == 'win32':
			process = subprocess.Popen(wincmd, stdout=outfile)
			process.wait()
			parse('./targets/' + ip + '/scan.txt', ip)
		else:
			subprocess.call(cmd, stdout=outfile)
			parse('./targets/' + ip + '/scan.txt', ip)


# Input an nmap scan file and an ip as a string. 
# 
# No output, calls populateDB().
#
# Parses the nmap output and builds strings in
# comma seperated lists based on ports, services, 
# and versions of the services found in the nmap scan.

def parse(file, ip):
	data = []
	with open(file) as scan:
			for line in scan:
				line = re.findall(r'([0-9]+)(\/)([a-z]+)(\s+)(open|filtered|closed)(\s+)(\S+)(\s+)(.+)', line)
				if line:
					data += line
			
	ports = ''
	services = ''
	versions = ''

	for row in range(len(data)):
		for column in range(len(data[0])):
			if column == 0:
				ports = ', '.join([ports, data[row][column]])
			if column == 6:
				services = ', '.join([services, data[row][column]])
			if column == 8:
				versions = ', '.join([versions, data[row][column]])

	populateDB(ip, ports, services, versions)


# Input an ip as a string, and a comma seperated list of ports, 
# services, and versions to be inserted into the database linked 
# to the entered ip.
# 
# No output.
# 
# Parses the entered strings, creates the hosts and services
# tables if they do not exist, and then enteres this data into the
# database.

def populateDB(ip, ports, services, versions):
	
	conn = sqlite3.connect(r'./machines.sqlite')
	c = conn.cursor()

	ports = ports.split(", ")
	services = services.split(", ")
	versions = versions.split(", ")

	c.execute("CREATE TABLE IF NOT EXISTS hosts(ip TEXT, possibleOS TEXT DEFAULT 'unknown',"\
			  "beenPwned integer DEFAULT 0, talksTo TEXT DEFAULT '',"\
			  "id integer PRIMARY KEY AUTOINCREMENT);")
	c.execute("CREATE TABLE IF NOT EXISTS services(id integer,"\
			  "port integer, service TEXT, version TEXT, FOREIGN KEY(id)"\
			  " REFERENCES hosts(id));")

	c.execute("INSERT INTO hosts(ip) VALUES(?)",\
			  (ip,))

	c.execute("SELECT id FROM hosts WHERE ip = ?",(ip,))
	
	ip_id = c.fetchone()
	ip_id = ip_id[0]
	
	for i in range(len(ports)):
		c.execute("INSERT INTO services (service, port, version, id) VALUES (?, ?, ?, ?)",\
			 	 (services[i], ports[i], versions[i], ip_id))


	c.execute("DELETE FROM services WHERE services.port IS NULL OR trim(services.port) = '';")


	conn.commit()
	conn.close()


# Input a query for the database as a string.
# 
# Output is the result of the query
# 
# Queries the database and returns the result.

def query(query):
	conn = sqlite3.connect(r'./machines.sqlite')
	c = conn.cursor()
	newQuery = validateQuery(query)
	c.execute(newQuery)
	#c.execute(query)
	table = c.fetchall()
	return table

def simpleQuery(query):
	conn = sqlite3.connect(r'./machines.sqlite')
	c = conn.cursor()
	c.execute(query)
	table = c.fetchall()
	return table


#The more efficient version
def validateQuery(input):
	if (len(input) == 1) & (input[0] == '*'):
		#allow user to see all information
		query = "select ip, port, service, version from hosts join services on hosts.id = services.id"
		return query
	query = "select ip, port, service, version from hosts join services on hosts.id = services.id where ip = '%s' or port = '%s' or service = '%s' or version = '%s'" % (input, input, input, input)
	return query


#Old version
def validateQuery2(input):
	q = input.split('.')
#if input is an ip address, check for its validity, then generate proper sql query that displays info for that ip
	if len(q) == 4:
		condition = True
		#below check if each block of ip falls under the range of 0-255
		for i in q:
			pattern = re.match('2[0-5][0-5]|1[0-9][0-9]|[0-9]$', i)
			if i == None:
				condition = False
				break
		if condition:
			ip = q[0] + '.' + q[1] + '.' + q[2] + '.' + q[3]
			query = "select ip, port, service, version from hosts join services on hosts.id = services.id where ip = '%s'" % ip
			return query
#if input is a port number, check for its validity, then generate proper query that lists all ip with that port open
	elif len(q) == 1: 
		if int(q[0]) <= 65535 & int(q[0]) >= 1:
			query = "select ip, port, service, version from hosts join services on hosts.id = services.id where port = '%s'" % q[0]
			return query


def setPwned(target):
	conn = sqlite3.connect(r'./machines.sqlite')
	c = conn.cursor()
	c.execute('update hosts set beenPwned = 1 where ip = "%s";' % target)
	conn.commit()
	conn.close()

def setTalks(target1, target2):
	conn = sqlite3.connect(r'./machines.sqlite')
	c = conn.cursor()
	target2 = ' ' + target2
	c.execute('update hosts set talksTo = talksTo || "%s" where ip = "%s";' % (target2, target1))
	conn.commit()
	conn.close()