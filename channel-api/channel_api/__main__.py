import os
import uvicorn

uvicorn.run('channel_api.main:app', host='0.0.0.0', port=os.environ.get('PORT', 8080))
