# 2rsystem repository

### Requirements

* tmux
* mosquitto
* python >= 3.6
* pip3

To install 2rsystem requirements, execute:

```bash
pip3 install -r requirements.txt
```

### Run

To run 2rsystem, execute:

```bash
make run
```

It will open a splitted tmux with all 2RSystem nodes and an instance of Mosquitto MQTT server.

You can run without tmux, just execute:

```bash
inv run -l info
```

`-l` option indicates the loglevel, `warning` (default), `info` and `debug`.

You can run a single node of the system, execute:

```bash
inv run -i kernel -l info
# or
inv run -i controller -l info
# or
inv run -i transmitter -l info
# or
inv run -i processor -l info
```

`WARNING`: make sure there is an instance of the Mosquitto running.

### Tests

You can test manually using:

```bash
inv run --log debug
inv faker --mqtt --timer 0.1
```

To run 2rsystem tests, execute:

```bash
pytest
```

It is necessary to start Mosquitto server to execute pytest.
