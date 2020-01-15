#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 09:26:00 2019

@author: rahul
"""

import socket, signal, cv2, sys, os
import numpy as np

HEADERSIZE = 20
IP = '127.0.0.1'
port = 1238

def keyboardInterruptHandler(signal, frame):
    print("Disconnected from server : " + IP + " " + str(port))
    exit(0)

def receive(client_socket):
    cv2.namedWindow("preview")
    new_msg = True
    full_msg = b''
    imageNo = 1
    while True:
        signal.signal(signal.SIGINT, keyboardInterruptHandler)
        try:
            msg = client_socket.recv(1024*256)
            full_msg += msg
            if new_msg:                
                try:
                    msg_len = int(full_msg[:HEADERSIZE].decode('utf-8'))
                    new_msg = False
                    
                except ValueError:
#                        print("Waiting...")
                    break
                    
            if len(full_msg) - HEADERSIZE >= msg_len:
                current_msg = full_msg[HEADERSIZE:HEADERSIZE+msg_len]
                next_msg = full_msg[HEADERSIZE+msg_len:]
                
                data = current_msg
                nparr = np.fromstring(data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
#                cv2.imwrite(os.path.join(os.getcwd() + "/Images/image{}.jpg".format(imageNo)), frame)
#                imageNo += 1
                
                cv2.imshow('preview', frame)                
                if cv2.waitKey(1) == 27:
                    client_socket.close()
                    sys.exit()

                new_msg = True
                full_msg = next_msg
                
        except socket.error as e:
            print(e)
            break
     
    cv2.destroyWindow("preview")

def run_client():    
    client_socket = socket.socket()
    client_socket.connect((IP, port))
    receive(client_socket)
    print("Disconnected from server : " + IP + " " + str(port))
    
if __name__ == '__main__':
    run_client()
