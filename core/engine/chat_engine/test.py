import os
from dotenv import load_dotenv
load_dotenv()


ES_API = os.environ['ES_API']
ES_CLOUD_ID = os.environ['ES_CLOUD_ID']

print('ES_API_KEY:', ES_API)
print('ES_CLOUD_ID:', ES_CLOUD_ID)
