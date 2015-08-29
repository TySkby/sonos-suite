# sonos-suite
A suite of tools for Sonos

Unfortunately (but perhaps unsurprisingly), Sonos doesn't have provide a controller application for Linux...
enter Sonos Suite!

Sonos Suite is built on top of the excellent [SoCo](http://python-soco.com) library, aimed specifically at
providing Linux users with handy tools to control their Sonos player(s) without needing to reach for a phone
or tablet.

Currently, Sonos Suite provides the following:
* A command-line interface
* A web API (more RPC than REST)

Additionally, some thoughts for the future:
* Curses-style terminal application
* A full-blown GTK GUI?

Let's begin, shall we?

## The CLI
The to use the Sonos Suite command-line interface, simply run `python runcli.py`.  
Of course, you won't get very far without some arguments.  Use `--help` to get the details, but in the meantime, here are some simple commands to get started:

* Send the "play" command to a single player (or speaker pair):

  `python runcli.py play --player Living Room`

* Then pause it:

  `python runcli.py pause --player Living Room`

* Send the "play" command to a group of players where the "Living Room" player is the group coordinator:

  `python runcli.py play --group Living Room`

Too much typing?  Here are a few tricks:

* Send the "play" command to the Living Room player:

  `python runcli.py play -p living`

* Then pause it:

  `python runclipy pause`

A few things are happening here:

1. Obviously, some shortcuts: `-p` for `--player` and `-g` for `--group`
2. The Sonos Suite CLI will remember the last player or group you sent a command to.  Unless you want to switch to a different group or player, there's no need to specify which player/group you want to control after you've done it once.
3. Perhaps the nicest feature here is the name-matching done automatically when given a player or group name to command.  When you specify a player, Sonos Suite takes a look at all the available player names and then finds the player whose name most closely matches the given value.  This is pretty nice for being able to quickly specify exactly what you want to control.  For example:
  * `living` matches `Living Room`
  * `bath` matches `Bathroom`
  * `bed` matches `Bedroom`, but watch out!  If you perhaps have multiple players with "Bedroom" in the name (for instance, "Master Bedroom" and "Guest Bedroom"), Sonos Suite will pick the first match it finds.  Keep things convenient and avoid ambiguity- `master` and `guest` would probably serve as better queries to search with 
in this case.

Pro Tip: Sonos group names are simply a comma-separated list of all players within that group, starting with the group coordinator.  So when giving a value for `--group`, you can name any speaker within the group and get a match.

Some especially helpful commands:

* See all available commands:

  `python runcli.py help`
* See documentation for a particular command (maybe you were wondering what "play" does?):

  `python runcli.py help play`

Last, but not least, here's a parting recipe of multiple commands.  Set a sleep timer at a nice, low volume for 30 minutes:

```
python runcli.py volume 10 -p bedroom
python runcli.py play
python runcli.py sleep 30
```

## The Web API
The Web API is an RPC-ish web service that functions very similarly to the CLI.

First, you need to start it:

* To run the server on port 80 listening on all interfaces:

  `python runserver.py  0.0.0.0 80`
* Or maybe just listen on localhost on port 9090:

  `python runserver.py localhost 9090`

Then, start making requests:

* The base path for the API is `/sonos-server`, so to play our "Living Room" speaker, we can make this request using **curl** (or just your browser):

  `curl -X GET 'http://localhost:9090/sonos-server/volume?player=Living%20Room'`
* Of course, the same name-matching functionality works for the Web API also:

  `curl -X GET 'http://localhost:9090/sonos-server/volume?player=living'`

* You can also make POST requests using JSON:

  `curl -X POST -H "Content-Type: application/json" -d '{"player": "Living Room"}' 'http://localhost:9090/sonos-server/volume'`

* Set the volume with a GET request:

  `curl -X GET 'http://localhost:9090/sonos-server/volume?player=living&args=30'`

* Or a POST request:

  `curl -X POST -H "Content-Type: application/json" -d '{"player": "Living Room", "args": [30]}' 'http://localhost:9090/sonos-server/volume'`

Finally, some documentation for using the Web API:

* Using GET:
  * The URL:
     * Base: `http://<server>:<port>/sonos-server`
     * Path: `/<command>`
  * Query string parameters:
      * **Required:** Set the player or group to control with a query string argument:
         * Group: `group=<name>`
         * Player: `player=<name>`
         * Note that `player` and `group` are mutually exclusive- if you include both, you'll get an error.
     * **Optional:** Provide any command arguments (use comma-separated values if you need to provide multiple arguments):
         * For example: `args=30` (use with `/volume` to set the volume to `30`)
* Using POST:
  * The URL (same as GET):
     * Base: `http://<server>:<port>/sonos-server`
     * Path: `/<command>`
  * The JSON payload:
      * **Required:** Set the player or group to control with a key/value pair:
         * Group: `"group": "<name>"`
         * Player: `"player": "<name>"`
      * **Optional:** Provide any command arguments as an indexed array:
         * For example: `"args": [30]` (use with `/volume` to set the volume to `30`)

* Example GET requests:
  * Play the "Kitchen, Dining Room" group:
      * URL: `http://localhost:9090/play?group=kitchen`
  * Check the volume of the "Kitchen" player:
      * URL: `http://localhost:9090/volume?player=kitchen`
  * Set the volume of the "Kitchen" player to 30:
      * URL: `http://localhost:9090/volume?player=kitchen&args=30`
* Example POST requests:
  * Play the "Kitchen, Dining Room" group:
      * URL: `http://localhost:9090/play`
      * Payload: `{"group": "kitchen"}`
  * Check the volume of the "Kitchen" player:
      * URL: `http://localhost:9090/volume`
      * Payload: `{"player": "kitchen"}`
  * Set the volume of the "Kitchen" player to 30:
      * URL: `http://localhost:9090/volume`
      * Payload: `{"player": "kitchen", "args": [30]}`

# Final comments
The Sonos Suite project is currently in its infancy.  Feel free to create an issue if you'd like to ask a question or make suggestions for improvement.

If you'd like to make a contribution, please do!  Fork and submit pull requests to your heart's desire.

Thanks, and enjoy!

# Etc.
The author:

* Author: Tyler Hendrickson 
* Email: hendrickson (dot) tsh (at) gmail (dot) com

Special thanks to...

The SoCo project maintainers for their great work:

* Website:  http://python-soco.com/
* GitHub: https://github.com/SoCo/SoCo

The Falcon project maintainers for their wonderful web framework:

* Website: http://falconframework.org/
* Github: https://github.com/falconry/falcon
