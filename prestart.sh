#!/usr/bin/env bash

set -e

echo "->$ Run migrations . . ."

cd ..

alembic upgrade head

# shellcheck disable=SC2164
cd friendly # TODO по идее в этом файле не должно быть cd

echo "->$ Migrations finished!"

exec "$@"