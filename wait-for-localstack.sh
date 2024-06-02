#!/bin/bash

set -e

host="localstack"
port="4566"

until nc -z "$host" "$port"; do
  >&2 echo "$host:$port is unavailable - sleeping"
  sleep 1
done

>&2 echo "$host:$port is available"
