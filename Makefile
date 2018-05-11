.PHONY: clean
clean:
	echo "cleaning no files"

# Each screen show
SCREEN_A := "mosquitto"
SCREEN_B := "inv run receiver"
SCREEN_C := "inv run controller"
SCREEN_D := "inv run transmitter"

run:
	$(shell tmux new-session -d && tmux split-window -d -t 0 -h)
	$(shell tmux split-window -d -t 0 -v)
	$(shell tmux split-window -d -t 2 -v)
	$(shell tmux send-keys -t 0 '/usr/bin/sh -c ${SCREEN_A}' enter)
	$(shell tmux send-keys -t 3 '/usr/bin/sh -c ${SCREEN_B}' enter)
	$(shell tmux send-keys -t 2 '/usr/bin/sh -c ${SCREEN_C}' enter)
	$(shell tmux send-keys -t 1 '/usr/bin/sh -c ${SCREEN_D}' enter)
	$(shell tmux attach)
