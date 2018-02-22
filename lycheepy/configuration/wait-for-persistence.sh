#!/bin/bash


# while ! echo exit | nc persistence 5432; do sleep 10; done
while ! timeout 1 bash -c "echo > /dev/tcp/persistence/5432"; do sleep 10; done
