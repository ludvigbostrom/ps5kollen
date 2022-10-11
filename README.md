# ps5kollen

The code behind the Twitter account https://twitter.com/ps5kollen

Scrapes several online stores for stock updates regarding ps5.

### How to run on your own
To run this you need to install requirements (preferably in a virtualenv)
```commandline
pip install -r requirements.txt
```
and fill in the constants in settings.

To run in docker:
```commandline
$ docker build -t ps5kollen .

Alternative 1:
$ docker run -it ps5kollen:latest bash
# python ps5kollen.py

Alternative 2:
$ docker run ps5kollen:latest python ps5kollen.py
```

To get the Twitter keys needed you have to have a Twitter account and a developer account.