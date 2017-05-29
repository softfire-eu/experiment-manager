#!/usr/bin/env bash
db_name=softfire

mysql -u root -p -e "drop database $db_name; create database $db_name"

python etc/generate_cork_files.py /etc/softfire/users
