# jupiter
An IRC bot that will monitor a list of nicks to jupe their nick.

###### Requirements
* [Python](https://www.python.org/downloads/) *(**Note:** This script was developed to be used with the latest version of Python.)*
* [PySocks](https://pypi.python.org/pypi/PySocks) *(**Optional:** For using the `proxy` setting.)*

###### Information
The bot has two options for juping nicks. The use of the `MONITOR` command, or the use of the `ISON` command.

The `MONITOR` command is an [IRCv3 feature](http://ircv3.net/specs/core/monitor-3.2.html) that is only supported by select IRCd's. With this command, you can add nicks to a monitor list that will have the server itself alert you when that nick becomes available, making jupes simple and fast.

The `ISON` command will be used as a fallback for servers that do not support the `MONITOR` command. With this command, a loop will run that issues the command for the nicks in your monitor list every 3 seconds, juping the first nick that become available. This method is not as quick as the `MONITOR` method and use a large amount of bandwidth. You may have to tinker with the throttle settings to avoid excess floods, etc.

Once the bot jupes a nick, it will lock in to that nick and stop monitoring for more nicks to jupe.

The bot will join a channel defined in the config and idle in there. This way you can run multiple bots on a network and be able to track them easily in the channel.

###### Commands *(Private Message)*
| Command | Description |
| --- | --- |
| .monitor | Enable monitoring. |
| .monitor list | Return the monitor list. |
| .monitor <+/-> \<nicks> | Add (+) or Remove (-) \<nicks> *(space separated)* from the monitor list. |
| .monitor reset | Remove all nicks from the monitor list.. |
| .status | Return current juped status. |