GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
GIT_DIFF=$(git diff)
GIT_REPO_NAME=$(basename -s .git `git config --get remote.origin.url`)

SIM_NAME=$1

echo $SIM_NAME

ssh ${REMOTE:="cypress-pc"} << EOF
    mkdir -p ~/.remote_builds
    cd ~/.remote_builds/${GIT_REPO_NAME}
    git checkout ${GIT_BRANCH}
    git reset --hard
    echo "$GIT_DIFF" | git apply
    cd hw/tb/$SIM_NAME
    make spinal
    make sim
EOF
