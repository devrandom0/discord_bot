#!/usr/bin/env python

import argparse
import os
import sys
import requests
import json
import socket

# because of multi-connection supprt, i use selector
# i could use threading, but after i searched, i chose selector
import selectors



# !!! check from step 0



# step 3
# send message to discord
def send_message(url, user, msg, emb_title=None, emb_txt=None):
    data = {}
    data["content"] = msg
    data["username"] = user

    if emb_title and emb_txt:
        data["embeds"] = []
        embed = {}
        embed["description"] = emb_txt
        embed["title"] = emb_title
        data["embeds"].append(embed)

    result = requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        if debug:
            print(json.dumps(data))
            print("Payload delivered successfully, code {}.".format(result.status_code))



# step 2
# parse received json from last function
# and set variables like alert name, status, description, ...
# and merge them together and send it to 'send_message' function
def alerter_parser(json_alert):
    # set variables empty
    alert_status, alert_alerts_status, alert_commonLabels_alertname, alert_commonAnnotations_description = "", "", "", ""


    alert_receiver = json_alert.get('receiver')
    alert_status = json_alert.get('status')

    if json_alert.get('alerts'):
        alert_alerts_status = json_alert['alerts'][0].get('status')

    if json_alert.get('groupLabels'):
        alert_groupLabels_alertname = json_alert['groupLabels'].get('alertname')
        alert_groupLabels_job = json_alert['groupLabels'].get('job')

    if json_alert.get('commonLabels'):
        alert_commonLabels_alertname = json_alert['commonLabels'].get('alertname')
        alert_commonLabels_instance = json_alert['commonLabels'].get('instance')
        alert_commonLabels_job = json_alert['commonLabels'].get('job')

    if json_alert.get('commonAnnotations'):
        alert_commonAnnotations_description = json_alert['commonAnnotations'].get('description')


    # merge message and set format or insert icon and send it to next function
    if alert_status.upper() == "FIRING":
        alert_status = alert_status + ' 🔥'
    elif alert_status.upper() == "RESOLVED":
        alert_status = alert_status + ' ✅'
    else:
        alert_status = alert_status + ' ℹ️'

    msg = alert_status.upper()
    emb_title = alert_commonLabels_alertname + ': ' + alert_alerts_status.upper()
    emb_txt = alert_commonAnnotations_description

    send_message(url, user, msg, emb_title, emb_txt)



# step 1
# listening and receiving messages from alertmanager in this function
def receive_message(host, port):
    # receive packet and open it with buffer
    def read(conn, mask):
        try:
            receive = conn.recv(buffer)
            if receive:
                # decode packet and split headers and body
                # and decode body by json
                # then send it to alerter_parser function to parse alerts

                # this ping/pong test
                conn.send(receive)

                data = receive.decode('utf-8')
                iterator = iter(data.split("\n"))
                for line in iterator:
                    if not line.strip():
                        break
                body = "\n".join(iterator)
                jdata = json.loads(body)
                alerter_parser(jdata)
            else:
                sel.unregister(conn)
                conn.close()
        except json.decoder.JSONDecodeError as err:
            print(f"{err}")
            return
        except UnicodeDecodeError as err:
            print(f"{err}")
            return

    # accepting connection and hanle it to 'read' function to parse packet data
    def accept(sock, mask):
        conn, addr = sock.accept()
        conn.setblocking(False)
        sel.register(conn, selectors.EVENT_READ, read)

    try:
        # open socket on network
        with socket.socket() as sock:
            sock.bind((host, port))
            sock.listen()
            print(f"Listen on {host}:{port}\n")
            sock.setblocking(False)
            # because of multi-connection supprt, i use selector
            # i could use threading, but after i searched, i chose selector
            sel.register(sock, selectors.EVENT_READ, accept)
            while True:
                events = sel.select()
                for key, mask in events:
                    callback = key.data
                    callback(key.fileobj, mask)

    except OSError as err:
    # except BaseException as err:
        print(f"{err}")



# step 0
if __name__ == "__main__":

    # call argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-U', '--url', help='webhook url', default=os.environ.get('URL', None), required=True)
    parser.add_argument('-H', '--host', help='listen address (default 0.0.0.0)', default=os.environ.get('HOST', "0.0.0.0"), required=False)
    parser.add_argument('-p', '--port', help='listen port (default 9481)', default=os.environ.get('PORT', 9481), required=False)
    parser.add_argument('-u', '--user', help='user in discord', default=os.environ.get('USER', 'Discord-Bot'), required=False)
    parser.add_argument('-d', '--debug', help='Enable debug mode', action='store_true')
    args = parser.parse_args()

    # buffer of receive 
    buffer = 65535

    # because of multi-connection supprt, i use selector
    # i could use threading, but after i searched, i chose selector
    sel = selectors.DefaultSelector()
    
    # set args to variables
    host = args.host
    port = args.port
    user = args.user
    url = args.url
    debug = args.debug

    # check if url not exist, exit
    if not url:
        print("webhook url doesn't exist.\n")
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    print(f"Debug mode is {debug}")

    # this is calling for test
    # send_message()
    # send_message(url, user, msg, emb_title=None, emb_txt=None)

    # first step: start listening to receive messages from alertmanager
    receive_message(host, port)