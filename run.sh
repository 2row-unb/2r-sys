#! /bin/bash

# Each screen
SCREEN_A="kernel"
SCREEN_B="controller"
SCREEN_C="transmitter"
SCREEN_D="processor"
SCREEN_E="kernelcontrol"

tmux new-session -d
tmux split-window -d -t 0 -v
tmux split-window -d -t 0 -v
tmux split-window -d -t 0 -h
tmux split-window -d -t 2 -h
tmux split-window -d -t 4 -h
tmux send-keys -t 0 "inv run $(echo $@) -i ${SCREEN_A}" enter
tmux send-keys -t 1 "inv run $(echo $@) -i ${SCREEN_B}" enter
tmux send-keys -t 2 "inv run $(echo $@) -i ${SCREEN_C}" enter
tmux send-keys -t 3 "inv run $(echo $@) -i ${SCREEN_D}" enter
tmux send-keys -t 5 "inv run $(echo $@) -i ${SCREEN_E}" enter
tmux send-keys -t 4 "inv flask" enter 
tmux attach
