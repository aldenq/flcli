# flcli
Further-Link Command Line Interface



The goal of this project is to allow access to Further-link via a command line interface. This can be used to allow you to remotely run projects on your Pi-top.




Usage:


flcli can be used simply as a command that allows you to run stuff on your Pi-Top, it can also be integrated into other IDE's such that by clicking the "run" button it will run the code on the pi-top rather then on the local machine.



examples:


 python3.8 flcli.py 127.0.0.1 helloworld.py
 
 python3.8 flcli.py 192.168.0.1 helloworld.py


 -c flag can be used to show syntax errors
 
 python3.8 flcli.py 192.168.0.1 helloworld.py -c
