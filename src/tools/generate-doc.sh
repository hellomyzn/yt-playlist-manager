#!/bin/bash -e

PROJECT_DIR="/opt/work"
PROJECT_NAME=$(echo $PROJECT_NAME)
SPHINX_DIR="/opt/docs/sphinx"

function show_usage() {
    cat << EOM
description:
    generate documents in ${SPHINX_DIR}/build/ by sphinx.

usage:
    $(basename $0) [OPTIONS]

options:
    -h, --help          show this commands usage and exit

example:
    $(basename $0)
EOM
}

function generate_api_doc() {
    set -x

    export PYTHONPATH=${PROJECT_DIR}

    rm -f ${SPHINX_DIR}/resources/*
    poetry run sphinx-apidoc -f -H ${PROJECT_NAME} -o ${SPHINX_DIR}/resources ${PROJECT_DIR}
    poetry run sphinx-build -b html ${SPHINX_DIR} ${SPHINX_DIR}/build

}

function main() {
    cd ${PROJECT_DIR}

    case $1 in
        "-h" | "--help")
            show_usage;;
        *)
            generate_api_doc;;
    esac

}

main $*
