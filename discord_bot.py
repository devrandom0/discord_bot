#!/usr/bin/env python

import argparse
import os
import sys
import requests
import json
import socket

import selectors
sel = selectors.DefaultSelector()



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
        print(json.dumps(data))
        print("Payload delivered successfully, code {}.".format(result.status_code))



def alerter_parser(json_alert):
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



def recive_message(host, port):
    def read(conn, mask):
        recived = conn.recv(buffer)
        if recived:
            conn.send(recived)

            data = recived.decode('utf-8')
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



    def accept(sock, mask):
        conn, addr = sock.accept()
        conn.setblocking(False)
        sel.register(conn, selectors.EVENT_READ, read)

    try:
        with socket.socket() as sock:
            sock.bind((host, port))
            sock.listen()
            print(f"Listen on {host}:{port}\n")
            sock.setblocking(False)
            sel.register(sock, selectors.EVENT_READ, accept)
            while True:
                events = sel.select()
                for key, mask in events:
                    callback = key.data
                    callback(key.fileobj, mask)

    except OSError as err:
    # except BaseException as err:
        print(f"{err}")



if __name__ == "__main__":

    # call argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', help='listen address (default 0.0.0.0)', default=os.environ.get('HOST', "0.0.0.0"), required=False)
    parser.add_argument('-p', '--port', help='listen port (default 9481)', default=os.environ.get('PORT', 9481), required=False)
    parser.add_argument('-u', '--user', help='user in discord', default=os.environ.get('USER', 'Discord-Bot'), required=False)
    parser.add_argument('-U', '--url', help='webhook url', default=os.environ.get('URL', None), required=False)
    args = parser.parse_args()

    buffer = 65535
    
    host = args.host
    port = args.port
    user = args.user
    url = args.url

    if not url:
        print("webhook url doesn't exist.\n")
        parser.print_help(sys.stderr)
        sys.exit(1)

    # send_message()
    # send_message(url, user, msg, emb_title=None, emb_txt=None)
    recive_message(host, port)