#! /bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

RC=0

DIRS=($SCRIPT_DIR/*)

for dir in ${DIRS[@]}; do
    if [ -d $dir ]; then
        printf "\n\n\nTesting $dir \n\n"
        cd $dir
        rm sim_build/results.xml &> /dev/null

        trap 'RC=1' ERR
        python test_*.py
        trap - ERR

        failed=$(grep -q "failure" "sim_build/results.xml")$?

        if [ $failed -eq 0 ]; then
            RC=1
        fi
    fi
done

exit $RC
