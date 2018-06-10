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

### RaspberryPi
To run 2rsystem, execute:

```bash
./run.sh
```

It will open a splitted tmux with all 2RSystem nodes. Make sure Mosquitto server is running before.

Also, you can run without tmux.

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

### Mock Raspberry on any Linux

If you try to execute 2RSystem out of a Raspberry, it'll crash. You can simulate the Raspberry behavior with the `rpi-mock` flag.

```bash
./run.sh --rpi-mock
```

Also, you can execute `inv run` with the same flag. 

```bash
inv run -i kernel -l info --rpi-mock
```

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
