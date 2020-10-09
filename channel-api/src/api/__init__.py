__version__ = '0.1.0'

from mangum import Mangum
from .main import app

handler = Mangum(app, enable_lifespan=False)
