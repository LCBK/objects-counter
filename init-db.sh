#!/bin/bash
user_exists=$(psql -U postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='lcbk'")
db_exists=$(psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='objects_counter'")
if [ "$user_exists" = "1" ]
then
    echo "User lcbk already exists"
else
    echo "Enter the database password: "
    read -s -r db_password
    psql -U postgres -c "CREATE USER lcbk WITH PASSWORD '$db_password';"
fi

if [ "$db_exists" = "1" ]
then
    echo "Database objects_counter already exists"
else
    psql -U postgres -c "CREATE DATABASE objects_counter OWNER lcbk;"
    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE objects_counter TO lcbk;"
fi
