<h1>Network Monitoring Tool</h1>

<p>In a network, there is one central PC (server) and all the other PCs in the network are monitored. All these PCs have USB connection, LAN connection and Internet connection. The tool should detect any connection made in real-time on the client PCs and also save the log of each PC. It is assumed all the PCs already know the IP address of the server.</p>
<p><b>Language Used: </b>Python</p>
<p><b>OS Requirement: </b> Any Linux Distribution</p>

<h2>Running the Code</h2>
<p>Download the entire repository locally.<p>
<p>Run server.py on the server PC.</p>
<p>On every other PC in the network which needs to be monitored, run main.py.</p>

<h2>Working</h2>

<h3>USB Transfer Detection</h3>
<p>When a USB device is connected to a linux machine, a kernel event is triggered which a device manager called udev (userspace /dev) listens to and executes the bash script usb_check.sh which logs into two different files which are log.txt and usb.log.</p>
<p>Then a cron job is run every minute which calls the python script usb.py, which checks for changes in usb.log and sends the data to the server in real time.</p>
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
<p>After   using   the   above   filters,   maximum   of   the   trackers   and microservices   are   removed.   The   IP   addresses   of   all   websites accessed  are  stored  in  log.txt  along  with  the  timestamp  in  each session.</p>


## Setup and working
connect a pendrive and check for the udeve kernel event
```bash
udevadm monitor
```
after that look for device type and subsystem from the output of
```bash
udevadm info /dev/sdb
```
then we need to perform some action when a usb event is detected so we need to add a rule, gernarally on all GNU/Linux distributons it is stored in /etc/udev/rules.d or /etc/lib/udev/rules.d the rule file is conventionally started with a number and the rules are processed in a numeric order.

create a new rule in one of the above directory and name it 99-usbdetect.rules 
```bash
SUBSYSTEM=="usb", ACTION=="add", ENV{DEVTYPE}=="usb_device", RUN+="/bin/usb_check.sh"
```
then type out the following command with super user privilages
```bash
udevadm control --reload
```
>the content must be simmilar with some changes depending on usb dasy chain or device id.

for this to work you must first move the usb_check.sh to bin and change it's permissions or change the script addresss in the above rule itself
```bash
mv usb_check.sh /bin/
chmod 751 /bin/usb_check.sh
```

for further reading refer the [udev page](https://wiki.archlinux.org/index.php/Udev) on [Arch wiki](https://wiki.archlinux.org/)  

the above code just tells the system to execute the usb_check.sh shell script which makes a log of all the usb events but dose't upload automatically to the server, it maintains two different logs one for the usb and a total log of all the events happening in the system regarding network.

the log.txt fiel esentially holds all of the logs so we need to push it to the server, we are doing it using a GNU utility called cron a shedule tasker, it calls a required task in periodically. for further reading refer the cron manual [cron manual](https://www.gnu.org/software/mcron/manual/html_node/Crontab-file.html)

```bash
crontab -l
crontab -e
* * * * * /usr/bin/python3 /path/to/usb.py
```
 the above thing executes every minute and checks for any changes in usb.log and sends them to server to check the changes
