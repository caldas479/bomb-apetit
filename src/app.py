import os

# App Initialization
from . import create_app # from __init__ file
app = create_app(os.getenv("CONFIG_MODE"))

# ----------------------------------------------- #

# Applications Routes
from .application import urls

# ----------------------------------------------- #
app.secret_key = 'your_secret_key_here' #TODO-GERAR ISTO PARA SER RANDOM EM TODAS AS VMS


if __name__ == "__main__":


    # flask run -h 192.168.2.10 -p 443 --cert=ssl/server.crt --key=ssl/server.key
    app.run(ssl_context=('ssl/server.crt', 'ssl/server.key'))
