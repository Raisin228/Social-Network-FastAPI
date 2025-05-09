#!/usr/bin/env bash

set -e

cd ..

echo "->$ Run data embeddings"

python scripts/load_values_db.py

echo "->$ Data embeddings complited!!"

echo "->$ Run migrations . . ."

alembic upgrade head

# shellcheck disable=SC2164
cd friendly # TODO по идее в этом файле не должно быть cd

echo "->$ Migrations finished!"

exec "$@"