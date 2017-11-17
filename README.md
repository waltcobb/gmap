# gmap
Gmap (guimap) is a network map visualization tool and network note keeper. 

Dependencies:<br>
  1. python3 (and the following modules):<br>
     - flask<br>
     - apscheduler<br>
  2. nmap<br>
     - linux/macOS:<br> 
       - git clone https://github.com/nmap/nmap.git (while in the gmap root directory) <br>
       - change directory into the nmap directory, then:
         - ./configure
         - make
         - make install
     - windows:<br>
       - install the nmap for windows into the project directory 'winmap' (https://nmap.org/dist/nmap-7.60-setup.exe)<br>

Once these dependencies have been satisfied, navigate to the project directory through your systems command line, and simply run the comman "python server.py". This will start the gmap server, open your web browser and navigate to "localhost:5000" to open the gmap GUI. Enter and ip address into the "ip" form, and press enter. You will now see this ip listed in the box labeled "IPs currently being scanned:" (this list is a que, where the ip on top is currently being scanned, and the ips in the list will be scanned from top to bottom). After the scan completes, the ip will disappear from the list and gmap will begin scanning the next ip in the list. Once an ip has been scanned, you can query the database for the scan results. This is done using the other, longer form. Currently full sql queries are needed to scan the database. The current schema is as follows:
 <br>
 <br>
  1. hosts<br>
     - ip<br>
     - possibleOS<br>
     - beenPwned<br>
     - talksTo<br>
     - id (primary key)<br>
   2. services<br>
      - id (foreign key)<br>
      - port<br>
      - service<br>
      - version<br>
