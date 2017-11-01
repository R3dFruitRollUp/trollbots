# efknockr
A mass flood script for IRC to attack a large number of networks and channels.

##### Requirements
* [Python](https://www.python.org/downloads/) *(**Note:** This script was developed to be used with the latest version of Python.)*
* [PySocks](https://pypi.python.org/pypi/PySocks) *(**Optional:** For using the `proxy` setting.)*

##### Information
For each server defined in `targets`, the bot will connnect, join all channels from a /LIST output, or specifically defined channels in the config, send each line from `msg.txt`, mass hilight everyone, and then part.