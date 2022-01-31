#!/bin/bash

killbg() {
    for p in "${pids[@]}" ; do
        echo "Killing $p"
        kill "$p";
    done
}

trap killbg EXIT
pids=()
cd backend/real_time/
python backend.py &
pids+=($!)
cd ../../prod-frontend
npm start
