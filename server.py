
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import request, Flask, render_template, jsonify
import gooeymap
import atexit
import time

scanQue = []
isScanning = False
app = Flask(__name__)


#set route for homepage
#linking html file from templates folder to homepage

@app.route("/")
def main():
	return render_template('./index.html') 


#set route for query
#take user input as q
#implement gooeymap module and take q as a parameter for its query function
#input the returned value into table variable and then link the table variable into 
#the table variable in the index.html file. It will display the query data

@app.route("/query")
def query():
	q = request.args.get('q', type=str)
	query = gooeymap.query(q)
	if len(query[0]) == 3:																		
		table = [dict(ip=row[0], port=row[1], service=row[2]) for row in query]					
	else:																						
		table = [dict(ip=row[0], port=row[1], service=row[2], version=row[3]) for row in query] 
	return render_template('./index.html', table = table) #linking the html file from templates folder


#set route for scan
#take user input as ip and append it into the queue (scanQue)

@app.route("/scan")
def scan():
	global scanQue
	arg = request.args.get('ip', type=str) #take user input
	if ' ' in arg:
		ips = arg.split()
		for target in ips:
			scanQue.append(target)
			print(target)
	else:
		print(arg)
		scanQue.append(arg)
	
	return render_template('./index.html')


#set route for showque 
#print out scanned data

@app.route("/showque")
def showque():
	global scanQue
	return jsonify(scanQue)

@app.route("/isscanning")
def checkScanning():
	global isScanning
	return jsonify(isScanning)

#If the queue is not empty and program is not currently scanning, 
#take global variable scanQue and input it into gooeymap scan function

def startScan():
	global isScanning
	print('arg=', scanQue)
	if (len(scanQue) != 0) and not isScanning:
		print('scanning')
		isScanning = True
		gooeymap.scan(scanQue[0])
		isScanning = False
		del scanQue[0]
		print('done')

@app.route("/graph")
def loadGraph():
	arg = request.args.get('g', type=str)
	data = gooeymap.query(arg)
	pwnedList = gooeymap.simpleQuery('select ip from hosts where beenPwned = 1')
	graph = 'dinetwork {'
	for host in range(len(data)):
		for info in range(len(data[0])):
			thing = str(data[host][info])		# set delimiters to allow javascript to read variables, changes back later.
			thing = thing.replace('-', '_DASH_')	# may find a more elegant way to fix this later.
			thing = thing.replace(';', '_SEMICOLON_')
			thing = thing.replace(':', '_COLON_')
			thing = thing.replace('(', '_OPENPAR_')
			thing = thing.replace(')', '_CLOSEPAR_')
			thing = thing.replace(' ', '_SPACE_')
			thing = thing.replace('+', '_PLUS_')
			graph += thing
			if info == 0:
				graph += ' -- '
			elif info != len(data[0]) - 1:
				graph += '_NEWLINE_'
		graph += ' ; '
	graph += '}'
	print('list', pwnedList)
	return render_template('./graph.html', graph = graph, pwned = pwnedList)


@app.route("/pwned")
def pwned():
	target = request.args.get('target', type=str) 
	gooeymap.setPwned(target)
	return render_template('./index.html')

@app.route("/talking")
def talks():
	target1 = request.args.get('target1', type=str) 
	target2 = request.args.get('target2', type=str) 
	gooeymap.setTalks(target1, target2)
	return render_template('./index.html')




#calls the startScan functino every 5 seconds

scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=startScan,
    trigger=IntervalTrigger(seconds=5),
    replace_existing=False)
atexit.register(lambda: scheduler.shutdown())

#if this file is called directly, run the program

if __name__ == '__main__':
   app.run() 

