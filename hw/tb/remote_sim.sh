GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
GIT_DIFF=$(git diff HEAD)
GIT_REPO_NAME=$(basename -s .git `git config --get remote.origin.url`)

SIM_NAME=${1%/}

if [ -z "${GIT_DIFF}" ]; then
    NO_PATCH="#"
fi

git diff HEAD > .patch

# Copy current repo state to remote
scp .patch ${REMOTE}:~/.remote_builds/${GIT_REPO_NAME}

# Run sim on remote
ssh ${REMOTE} /bin/bash << EOF
    cd ~/.remote_builds/${GIT_REPO_NAME} &&
    source venv/bin/activate &&
    git reset --hard &&
    git pull &&
    git checkout ${GIT_BRANCH} &&
    ${NO_PATCH:=''}git apply .patch &&
    cd hw/tb/$SIM_NAME &&
    make spinal &&
    make sim
EOF

SUCCESS=$?

if [ $SUCCESS -eq 0 ]; then
    # Copy fst file back
    mkdir -p ./${SIM_NAME}/sim_build
    scp "${REMOTE}:~/.remote_builds/${GIT_REPO_NAME}/hw/tb/${SIM_NAME}/sim_build/"'*.fst' ./${SIM_NAME}/sim_build/.
    scp "${REMOTE}:~/.remote_builds/${GIT_REPO_NAME}/hw/tb/${SIM_NAME}/sim_build/"'*.png' ./${SIM_NAME}/sim_build/.
fi

exit $SUCCESS
