Daemon package
==============


Description
-----------
Daemon class to turn any program into an UNIX daemon process.
Inspired from "Launching a Daemon Process on Unix"
http://chimera.labs.oreilly.com/books/1230000000393/ch12.html#_discussion_209


Getting started
---------------
```
from daemon import Daemon
def run():
    while True:
        #do something

test = Daemon('/temp/test.pid', action=run,
              stdout='/var/log/test.log', stderr='/var/log/test.log')
test.start()
```

Import command line arguments:
```
if __name__ == '__main__':
    test.commands()
```

Another option to run the daemon
(from class heritage):
```
from daemon import Daemon
class Test(Daemon):
    def run(self):
        while True:
            #do something

test = Test('/temp/test.pid', stdout='/var/log/test.log', stderr='/var/log/test.log')
test.start()
```


License
-------
Sylvain Carlioz
August, 2017
MIT License
