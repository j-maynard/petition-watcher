# Peition Watcher

If you've ever wanted to track the status of a governement petition
on your Desktop then this is the python script for you.  Its a simple
Python3/TKinter script which loads data directly off the 
partitions.gov.uk web site.

# Running the script

Running the script is very simple.  You can open the script in IDLE3
on MacOS, Windows or Linux and select Run > Run Module (F5).
Alternative the script can be run from the command line. 

```
$ chmod +x python-watcher.py
$ ./pythin-watcher.py
```

You'll get a root window with a list of open petitions.  Look through
the list, find the peition you wish to watch and double click it.  This
will bring up a new window with the count, the peitions action and
if you click the info button you can see the description of the 
peittion.

# Future Development

Enable command line options for refresh, thread pool count and improve
the user interface of the root window where you select a petition.

# License

This script is made available under an MIT License.
