# Base image for database
FROM postgres:10

# Make sure we have git
RUN apt-get update
RUN apt-get install -y git-core

# Create workdir
WORKDIR /db

# Checkout the server 
COPY ./sql /db/sql

# Generate a script that will initialize the database
RUN echo "psql -c 'create database admin_db;'" > /docker-entrypoint-initdb.d/init.sh
RUN echo "psql -c 'create user admin_user;'" >> /docker-entrypoint-initdb.d/init.sh
RUN echo "psql -c 'grant all privileges on database admin_db to admin_user;'" >> /docker-entrypoint-initdb.d/init.sh
RUN echo "psql -d admin_db -U admin_user -a -f /db/sql/init_db_users.sql" >> /docker-entrypoint-initdb.d/init.sh
RUN echo "psql -d admin_db -U admin_user -a -f /db/sql/init_db.sql" >> /docker-entrypoint-initdb.d/init.sh

