import os
import json
import systemTest


   
# import requests
if os.environ.get('AWS_SAM_LOCAL') and os.environ.get('DEBUG') == 'true':
    import ptvsd

    # Enable ptvsd on 0.0.0.0 address and on port 5890 that we'll connect later with our IDE
    ptvsd.enable_attach(address=('0.0.0.0', 5890), redirect_output=True)
    ptvsd.wait_for_attach()


def lambda_handler(event, context):
    

    if event['action'] == 'runTest':
        return systemTest.runTest()

    raise Exception("Nothing Returned. Unmapped Event") 
   
