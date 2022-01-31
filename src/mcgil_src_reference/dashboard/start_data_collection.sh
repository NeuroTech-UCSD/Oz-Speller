#!/bin/bash

killbg() {
    for p in "${pids[@]}" ; do
        echo "Killing $p"
        kill "$p";
    done
}

trap killbg EXIT
pids=()
cd backend/data_collection/
python webapp_backend.py &
pids+=($!)
cd ../../prod-frontend
npm start
