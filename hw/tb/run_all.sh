#!/bin/bash
# One regression entry point. Explicit exclusions are printed, never counted as passes.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" && pwd )
pass=()
fail=()
skip=()
for dir in "$SCRIPT_DIR"/*/; do
    name=$(basename "$dir")
    [[ "$name" == template ]] && continue
    if [ "$#" -gt 0 ] && [[ " $* " != *" $name "* ]]; then continue; fi
    if [[ " ${SKIP_TESTS:-} " == *" $name "* ]]; then
        skip+=("$name")
        continue
    fi
    tests=("$dir"/test_*.py)
    [ -f "${tests[0]}" ] || continue
    results="$dir/sim_build/results.xml"
    rm -f "$results"
    echo "Running $name"
    if (cd "$dir" && python "$(basename "${tests[0]}")") && \
        python "$SCRIPT_DIR/../../scripts/check_results.py" "$results"; then
        pass+=("$name")
    else
        fail+=("$name")
    fi
done
for name in "$@"; do
    [ -d "$SCRIPT_DIR/$name" ] && [ "$name" != template ] || fail+=("unknown:$name")
done
echo "PASS (${#pass[@]}): ${pass[*]}"
echo "FAIL (${#fail[@]}): ${fail[*]}"
echo "SKIP (${#skip[@]}): ${skip[*]}"
[ ${#fail[@]} -eq 0 ] && [ ${#pass[@]} -gt 0 ]
