# 5000
SAJOIN Flood IRC Bot

##### Requirements
* [Python](https://www.python.org/downloads/) *(**Note:** This script was developed to be used with the latest version of Python.)*
* [PySocks](https://pypi.python.org/pypi/PySocks) *(**Optional:** For using the `proxy` setting.)*

##### Information
This bot requires network operator privledges in order to use the `SAJOIN` command.

If `use_anope_svsjoin` is enabled, the bot will require services operator privledges with Anope in order to use the `SVSJOIN` command that OperServ provides, instead of `SAJOIN`.

The bot will idle in the **#5000** channel and a channel defined in the config.

Anyone who joins the **#5000** channel will be force joined into 5000 random channels.

It will announce in the channel defined in the config who joins the **#5000** channel.

The command `.kills` can be used to see how many people have been 5000'd.