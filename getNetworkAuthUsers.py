'''
List the users configured under Meraki Authentication for a network (splash guest 
or RADIUS users for a wireless network, or client VPN users for a wired network)
'''
        
import os
import asyncio
import meraki.aio
from datetime import datetime
from mongodbConnection import connect_mongo
from dotenv import load_dotenv, find_dotenv

# Load and get environment variables
load_dotenv(find_dotenv())
api_key = os.environ.get("API_KEY")
org_id = os.environ.get("ORGANIZATION")

async def get_users(aiomeraki: meraki.aio.AsyncDashboardAPI, network):
    try:
        users = await aiomeraki.networks.getNetworkMerakiAuthUsers(network['id'])
    except meraki.APIError as e:
        print(f'Meraki API error: {e}')
    except Exception as e:
        print(f'some other error: {e}')  
    else: 
        # Create the auth users meraki MongoDB data
        if users:
            connect_mongo(data='AuthUsers', collection=f'{net["name"]} ', content=users) 
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
        print(f'Analyzing Osasco:')
        # Get list of networks in organization
        try:
            networks = await aiomeraki.organizations.getOrganizationNetworks(org_id)
        except meraki.AsyncAPIError as e:
            print(f"Meraki API error: {e}")
        except Exception as e:
            print(f"some other error: {e}")

        # Create a list of all networks in the organization so we can call them all concurrently
        networkClientsTasks = [get_users(aiomeraki, net) for net in networks]
        for task in asyncio.as_completed(networkClientsTasks):
            networkname = await task
            print(f"Finished network: {networkname}")

if __name__ == "__main__":
    start_time = datetime.now()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    end_time = datetime.now()
    print(f'Script complete in {end_time - start_time}')
    

