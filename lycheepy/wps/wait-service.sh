#!/bin/bash


HOST=$1
PORT=$2
TIME=10

while ! timeout 1 bash -c "echo > /dev/tcp/${HOST}/${PORT}"; do sleep ${TIME}; done
