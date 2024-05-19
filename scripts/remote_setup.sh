GIT_REMOTE=$(git ls-remote --get-url origin)
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
GIT_REPO_NAME=$(basename -s .git `git config --get remote.origin.url`)

ssh ${REMOTE:="cypress-pc"} << EOF
    mkdir -p ~/.remote_builds
    cd ~/.remote_builds
    git clone ${GIT_REMOTE}
    cd ${GIT_REPO_NAME}
    git checkout ${GIT_BRANCH}
EOF
