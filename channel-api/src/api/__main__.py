import os
import uvicorn

uvicorn.run('src.api.main:app', host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), reload=True)
