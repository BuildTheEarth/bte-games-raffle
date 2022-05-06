## BTE Games Raffle Website

This is the raffle website for bte games

It works, but not ideal for the following:

- Computation that could be done on the client is done on the server
- Randomness is determined on server
- Dangerous use of jinja templating
- Horrible js code practices

Usage:

- Ideally do not, but if you want to, you can use the following:
- rename _config.json to config.json and fill the fields
- run init.py
- run the flask server on app.py