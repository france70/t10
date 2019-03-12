Actually not a bot, just Telegram client application for removing messages at 01.00 AM every day.

Before starting phone number should be determined in condif.py (`PHONE_NUMBER`).
Bot should be launched in interactive mode with mounting to local directory for saving .session-file, for example:

`docker build --tag=msg_remover .`

`docker run -v (pwd):/app -ti msg_remover`

You can type `--remove-now` (`-r`) argument: bot only remove messages and stop.
