#! /bin/bash

# Each screen
SCREEN_A="kernel"
SCREEN_B="controller"
SCREEN_C="transmitter"
SCREEN_D="processor"

tmux new-session -d && tmux split-window -d -t 0 -h
tmux split-window -d -t 0 -v
tmux split-window -d -t 2 -v
tmux send-keys -t 0 "inv run $@ -i ${SCREEN_A}" enter
tmux send-keys -t 1 "inv run $@ -i ${SCREEN_A}" enter
tmux send-keys -t 2 "inv run $@ -i ${SCREEN_A}" enter
tmux send-keys -t 3 "inv run $@ -i ${SCREEN_A}" enter
tmux attach
