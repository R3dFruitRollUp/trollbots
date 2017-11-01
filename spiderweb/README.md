# spiderweb
SAJOIN Trap Channel IRC Bot

##### Requirements
* [Python](https://www.python.org/downloads/) *(**Note:** This script was developed to be used with the latest version of Python.)*
* [PySocks](https://pypi.python.org/pypi/PySocks) *(**Optional:** For using the `proxy` setting.)*

##### Information
This bot requires network operator privledges in order to use the `SAJOIN` command.

If `use_anope_svsjoin` is enabled, the bot will require services operator privledges with Anope in order to use the `SVSJOIN` that OperServ provides, instead of `SAJOIN`.

The bot will idle in the channel defined in the config. Anyone who tries to part from the channel will be force joined back into it.