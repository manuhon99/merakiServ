'''
Testing multi thread
'''

import threading
import os
import asyncio
import meraki.aio
from datetime import datetime
from mongodbConnection import connect_mongo
from dotenv import load_dotenv, find_dotenv

import getClientsConnectivityEvents
import getClientsTrafficHistory

def networkClients():  
    while True:
        print("Info clientes %s" % threading.current_thread())
        #getClientsConnectivityEvents.clientsConnectivityEvents()

 
def clientsTaffic():
    while True:
        print("Info Tráfego %s" % threading.current_thread())
        #getClientsTrafficHistory.clientsTrafficHistory()
    
def run_threaded(do_func):
    job_thread = threading.Thread(target=do_func)
    job_thread.start()
    

def main():
    run_threaded(networkClients)
    run_threaded(clientsTaffic)

main()

 

