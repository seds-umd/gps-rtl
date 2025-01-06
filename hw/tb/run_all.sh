#! /bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

RC=0

# Catch errors
trap 'RC=1' ERR

DIRS=($SCRIPT_DIR/*)

for dir in ${DIRS[@]}; do
    if [ -d $dir ]; then
        printf "\n\n\nTesting $dir \n\n"
        cd $dir
        rm sim_build/results.xml &> /dev/null
        python test_*.py

        if grep -q "failure" "sim_build/results.xml"; then
            RC=1
        fi
    fi
done

exit $RC
