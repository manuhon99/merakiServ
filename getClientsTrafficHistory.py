'''
Get network clients traffic history
'''
  
import os
import math
import asyncio
import meraki.aio
from datetime import datetime
from mongodbConnection import connect_mongo
from dotenv import load_dotenv, find_dotenv

# Load and get environment variables
load_dotenv(find_dotenv())
api_key = os.environ.get("API_KEY")
org_id = os.environ.get("ORGANIZATION")

epoch = math.trunc(datetime.now().timestamp())

async def get_clients_traffic(aiomeraki: meraki.aio.AsyncDashboardAPI, network, client):
    try: 
        # Get client traffic history, until the endingBefore epoch parameter (or startingAfter - noticed that returns only by the day after you set)
        traffic = await aiomeraki.networks.getNetworkClientTrafficHistory(
                network['id'], 
                client['id'],
                perPage=1000,
                startingAfter=(epoch-(60*60*24))
                )
    except meraki.APIError as e:
        print(f"Meraki API error: {e}")
    except Exception as e:
        print(f"some other error: {e}")
    else:
        # Create the clients traffic history MongoDB data
        if traffic:
            connect_mongo(data='ClientTraffic', collection=f'{network["name"]} {client["id"]}', content=traffic)
    return network["name"], client["id"]

async def listNetworkClients(aiomeraki: meraki.aio.AsyncDashboardAPI, network):
    #print(f'Finding clients in network {network["name"]}')
    try:
        # Get list of clients on network, filtering on set timespan (60 seconds)
        clients = await aiomeraki.networks.getNetworkClients(
            network["id"],
            timespan=30 ,
            perPage=1000,
            output_log=False,
            total_pages="all",
        )
    except meraki.AsyncAPIError as e:
        print(f"Meraki API error: {e}")
    except Exception as e:
        print(f"some other error: {e}")
    '''
    else:
        if clients:
            connect_mongo(data='Clientes', collection=f'{network["name"]} ', test=clients)         
    '''
    # Create a list of all clients in the network so we can call them all concurrently
    clientsTasks = [get_clients_traffic(aiomeraki, network, client) for client in clients]
    for task in asyncio.as_completed(clientsTasks):
        clientname = await task
        #print(f"Finished client: {clientname}")       
    return network["name"]

async def main():
    # Instantiate a Meraki dashboard API session
    # NOTE: you have to use "async with" so that the session will be closed correctly at the end of the usage
    async with meraki.aio.AsyncDashboardAPI(
            api_key,
            base_url="https://api.meraki.com/api/v1",
            output_log=False,
            print_console=False,
    )  as aiomeraki:      
        #print(f'Analyzing Osasco:')

        # Get list of networks in organization
        try:
            networks = await aiomeraki.organizations.getOrganizationNetworks(org_id)
        except meraki.AsyncAPIError as e:
            print(f"Meraki API error: {e}")
        except Exception as e:
            print(f"some other error: {e}")

        # Create a list of all networks in the organization so we can call them all concurrently
        networkClientsTasks = [listNetworkClients(aiomeraki, net) for net in networks]
        for task in asyncio.as_completed(networkClientsTasks):
            networkname = await task
            #print(f"Finished network: {networkname}")

if __name__ == "__main__":
    start_time = datetime.now()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    end_time = datetime.now()
    print(f'Script complete in {end_time - start_time}')
    
