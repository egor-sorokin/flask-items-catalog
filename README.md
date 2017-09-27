# Item catalog application

## How to run the project:

Install virtual machine:
Fork/clone the repository https://github.com/udacity/fullstack-nanodegree-vm
Go to:
 ```sh
$ cd [project-dir]/vagrant
$ vagrant up
```

Put this project in a directory "[project-dir]/vagrant", then to run the app:
 ```sh
$ cd [project-dir]/vagrant
$ vagrant ssh
```

And now you are in a virtual machine

Firstly, prepare fake data:
 ```sh
$ cd /vagrant/catalog
$ python fake_data.py
```

Secondly, run the project:
 ```sh
$ cd /vagrant
$ python views.py
```

And go to "http://localhost:5000/"


Project structure:
- static - here are located all static files
- templates - a directory for all templates (html files)
- models.py - here are located database tables
- views.py - a file for api endpoints
- fake_data.py - a set of data to fill db tables
- client_secrets.json - credentials of client
