# Welcome to the Database Virtual Machine Walkthrough

Since we are running on a Kali machine we already have PostgreSQL installed, but we still need to do some configurations

## 1. Enable PostgreSQL on your machine

To enable the service input this command:

`$ sudo systemctl start postgresql`

To configure it to enable on system startup, do:

`$ sudo systemctl enable postgresql`

## 2. Configure a Password For The Postgres User

Switch to the root user of your machine (or simply type `sudo` before each command) with:

`$ sudo su`

Enter in the PostgreSQL shell. This command enters in the shell with the default user (postgres).

`$ sudo -u postgres psql`

In the shell we need to change the postgres default password, so we can connect with our code.

`ALTER USER postgres WITH PASSWORD 'postgres';`

## 3. Create the BombAppetit Database and grant access to the user just created

In order to create the database that our code connects to do.

`CREATE DATABASE bombappetit;`

Now to add privileges to the user you want to connect from do.

`GRANT ALL PRIVILEGES ON DATABASE bombappetit TO postgres;`

## 4. Generate the key to use in SSL certificates

In this step of the tutorial we are going to generate 2 certificates and 1 key.

In order to know where to generate these certificates to we need to know the data directory of our PostgreSQL service. (This needs to be done in the Postgres shell)

`SHOW data_directory;`

After doing this change the directory to the one outputed by that command. In my case

`cd /var/lib/postgresql/16/main`

Generate the server key with OpenSSL as follows

`openssl genrsa -aes128 2048 > server.key`

When prompted by the passphrase insert `sirs`, only so you can remember it afterwards.

After all we are going to use it now when we remove the passphrase

`openssl rsa -in server.key -out server.key`

In order to increase the security, assign read-only permissions of the private-key to the root user

`chmod 400 server.key`

set the ownership of the key to postgres user and group

`chown postgres:postgres server.key`

## 5. Generate Server Certificate

Generate a self-signed certificate with the private key.

`openssl req -new -key server.key -days 365 -out server.crt -x509`

As we are using a self-signed certificate we need to make it the root certificate so we can thrust it.

`cp server.crt root.crt`

## 6. Configure the SSL settings in PostgreSQL

Change the directory to where the PostgreSQL configurations lie.

`cd /etc/postgresql/16/main`

Alter the file `postgresql.conf` with nano/vim/etc

In the **Connection Settings**, search the **listen_addresses** setting and uncomment it as follows to allow connections from all hosts.

`listen_addresses = '*'`

In the same file, go to the SSL section and uncomment these settings and change the values as shown.

`ssl = on`

`ssl_ca_file = 'root.crt'`

`ssl_cert_file = 'server.crt'`

`ssl_crl_file = ''`

`ssl_key_file = 'server.key'`

`ssl_ciphers = 'HIGH:MEDIUM:+3DES:!aNULL' # allowed SSL ciphers`

`ssl_prefer_server_ciphers = on`

Now we´re going to alter the `pg_hba.conf` file as follows.

In the **IPv4 local connections**, change the line to allow connections from the hosts you want to connect to Postgres.

`hostssl    all           all           192.168.1.1/24          md5`

`hostssl    all           all           192.168.0.100/24          md5`

Save these changes and restart the postgres service.

`sudo systemctl restart postgresql`







