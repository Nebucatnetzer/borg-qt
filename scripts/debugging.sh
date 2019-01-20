#!/bin/bash
source venv/bin/activate

sigint_handler()
{
    kill $PID
    exit
}

trap sigint_handler SIGINT

cd borg_qt
while true; do
    ./borg_qt.py &
    PID=$!
    echo "---- Press Crtl+C to stop debugging. ----"
    inotifywait -e modify -e move -e create -e delete -e attrib --exclude '.*(/\.|_flymake\.py)' -r `pwd`
    sleep 0.5
    kill $PID
done
