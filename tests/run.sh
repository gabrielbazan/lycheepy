#!/bin/bash

set -e


VIRTUALENV=venv
REQUIREMENTS=requirements.txt
BIN=./${VIRTUALENV}/bin
PIP=${BIN}/pip
PYTHON=${BIN}/python


prepare() {
    echo "Preparing virtualenv ..."
    virtualenv ${VIRTUALENV}
    ${PIP} install -r ${REQUIREMENTS}
}


run() {
    echo "Running suites ..."
    for suite in test_*.py
    do
        echo "  Running ${suite} suite ..."
        ${PYTHON} ${suite}
    done
}


clean() {
    echo "Removing virtualenv ..."
    rm -fr ${VIRTUALENV}
}


prepare
run
clean

echo "Done!"

