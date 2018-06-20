# 2rsystem repository

### Requirements

* tmux
* emqtt with emq_sn enabled
* python >= 3.6
* pip3

To install 2rsystem requirements, execute:

```bash
pip3 install -r requirements.txt
```

### Environment configuration

1. Download and install http://emqtt.io/
2. Run emqtt.
  ```bash
  emqttd console
  ```
3. Edit emq_sn with custom configurations:
  ```
  # emq_sn.conf

  mqtt.sn.port = 1885
  mqtt.sn.advertise_duration = 900
  mqtt.sn.gateway_id = 1
  mqtt.sn.enable_stats = off
  mqtt.sn.enable_qos3 = off
  mqtt.sn.predefined.topic.0 = reserved
  ```
4. Enable emq_sn plugin
  ```bash
  ./emqttd_ctl plugins load emq_sn
  ```

5. Reload emqttd if necessary.

### Run

### RaspberryPi
To run 2rsystem, execute:

```bash
./run.sh
```

It will open a splitted tmux with all 2RSystem nodes. Make sure MQTT server is running before.

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
# or
inv run -i kernelcontrol -l info
```

### Mock Raspberry on any Linux

If you try to execute 2RSystem out of a Raspberry, it'll crash. You can simulate the Raspberry behavior with the `rpi-mock` flag.

```bash
./run.sh --rpi-mock --log debug
```

Also, you can execute `inv run` with the same flag. 

```bash
inv run -i kernel -l info --rpi-mock
```

### Tests

You can test manually using:

```bash
inv run --log debug
inv faker --mqttsn --timer 0.1  # if you are using MQTT-SN in kernel
inv faker --mqtt --timer 0.1    # if you are using MQTT in kernel
```

To run 2rsystem tests, execute:

```bash
pytest
```

It is necessary to start MQTT server to execute pytest.
