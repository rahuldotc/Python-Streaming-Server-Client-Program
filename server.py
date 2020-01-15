#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 08:27:29 2019

@author: rahul
"""

import socket, time, threading, signal, cv2

connect_lock = threading.Lock()
HEADERSIZE = 20
connect_sockets = {}
addresses = []
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def disconnect():
    for address in addresses:
        connect_sockets[address].close()
        del connect_sockets[address]
    
    print("Shutting down server")

def keyboardInterruptHandler(signal, frame):    
    disconnect()
    exit(0)
    
def video_stream():    
    vc = cv2.VideoCapture(0)
    if vc.isOpened():
        rval, frame = vc.read()
    else:
        rval = False
        
    while rval:
        #encoding the frame and prefixing it with a length header
        data = cv2.imencode('.jpg', frame)[1].tostring()
        data = f'{len(data):<{HEADERSIZE}}'.encode('utf-8') + data
        
        #code for transmitting the encoded frame to all clients
        connect_lock.acquire()
        for address in addresses:
            try:
                connect_sockets[address].send(data)
            except socket.error:
                connect_sockets[address].close()
                addresses.remove(address)
                del connect_sockets[address]
                print("Client : {} disconnected".format(address))
                
        connect_lock.release()
        
        #Reading the next frame
        rval, frame = vc.read()
        key = cv2.waitKey(1)
        if key == 27:
            break
    
    vc.release()
    
def accepting_connections():
    while True:
        conn, addr = server_socket.accept()
        
        connect_lock.acquire()
        connect_sockets[addr] = conn
        addresses.append(addr)
        connect_lock.release()
        
        print('connection established with {} at {}'.format(addr, round(time.time())))

def run_server():
    IP = '192.168.0.15'
    port = 1238
    
    server_socket.bind((IP, port))
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.listen(5)
   
    video_thread = threading.Thread(target=video_stream, args=())
    accept_thread = threading.Thread(target=accepting_connections, args=())
    
    video_thread.start()
    accept_thread.start()
    
    signal.signal(signal.SIGINT, keyboardInterruptHandler)
    
    
if __name__ == '__main__':
    run_server()
