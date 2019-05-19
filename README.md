<h1>Network Monitoring Tool<h1>
<p><b>Language Used:</b> Python</p>
<p><b>OS Requirement: Any Linux Distribution</b></p>
<h2>Aim:</h2>
<p>In a network, there is one central PC (server) and all the other PCs are monitored. These PCs have USB connection, LAN connection and Internet connection. The tool detects any connection made in real-time and also stores a log of each PC.</p>
<h2>Running the Code</h2>
<p>Download the entire repository locally<p>
<p>Run server.py on the server PC</p>
<p>On every other PC which needs to be monitored, run main.py</p>

<h2>Working</h2>

<h3>USB Transfer Detection</h3>
<p>When a USB device is connected to a linux machine, a kernel event is triggered which a device manager called udev (userspace /dev) listens to and executes a bash script given below which logs into two different files which are log.txt and usb.log.</p>
<p>Then a cron job is run every minute which calls a python script which checks for changes in usb.log and sends the data to the server in real time.</p>
<p>The  USB  event  is  logged  in  log.txt which  contains  the  log  of  all  the transfer events happening in the client PC.</p>

<h3>Packet Sniffing</h3>
<p>To  detect  LAN  transfers  and  internet  transfers,  a  socket  is  created which receives all incoming packets to the client PC. By running np.py, these packets are unpacked using structs and information such as the protocol  number,  source  and  destination  MAC  addresses  of  the packets  are  retrieved.  By  setting  the  protocol  number  as  8,  ARP packets are filtered and only IPv4 packets are considered.</p>
<p>By using structs again, IP protocol, the source IP, destination IP and the data present in the IPv4 packet can be extracted. The IP protocols of 6 (TCP) and 17 (UDP) are important and necessary for detection of LAN and internet transfers.</p>

<h3>LAN Transfer Detection</h3>
<p>The source and destination IPs of the incoming TCP/UDP packets are checked.   If   both   belong   to   the   same   private   network   (with   IP Addresses  172.16-31.*.*  or  192.168.*.*  ),  then  the  transfer  which happened is a LAN transfer.</p>
<p>The  packets  are  read  till  the  no  other  LAN  packets  are  received between both the PCs for a time duration of 2 seconds. Then it can be concluded that the transfer has completed.</p>
<p>Both  the  source  and  destination  IPs  of  the  packets  involved  in  the transfer are logged and saved in log.txt of both the client PCs.</p>

<h3>Internet Transfer Detection</h3>
<p>If  the  TCP/UDP  packets  received  by  the  client  PC  are  in  the  port number 443 (default HTTPS port) or 80 (default HTTP port) and the destination IP is not from a private network, then the transfer is an internet transfer.</p>
<p>The  IP  addresses   of  microservices   and  trackers   from  Microsoft, Amazon AWS, Google Cloud and Bharati Airtel are first filtered. These IP addresses are present directly in the Amazon Cloud website and are also filtered by observing the traffic manually. These IP families and stored in the file ip.txt.</p>
<p>After   using   the   above   filters,   maximum   of   the   trackers   and microservices   were   removed.   The   IP   addresses   of   all   websites accessed  are  stored  in  log.txt  along  with  the  timestamp  in  each session.</p>
