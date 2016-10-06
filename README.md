
## Synopsis
Set of tools to snapshot & analyse procfs of a unix machine.

 - shapshot.py: a tool to snapshot statistics from a (remote) unix machine.
 - webserver.py: webserver useful for result analysis.

## Installation
Currently this project does not require installation.
Required Python depencencies:
 - paramiko (for SSH logins)
 - twisted (for graphical view of results)

On a Debian they can be installed calling:
```
  sudo apt-get install python-paramiko python-twisted
```

or
```
pip install -r requirements.txt
```


## License
Apache License, Version 2.0, January 2004
http://www.apache.org/licenses/


