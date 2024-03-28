# Flask User Account Management

This is a Flask application for user account management with features like account creation, login, key registration, and PGP key signing.

## Table of Contents

- [Flask User Account Management](#flask-user-account-management)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
  - [Install Python dependencies](#install-python-dependencies)
  - [Running the Application](#running-the-application)
  - [Usage](#usage)
  - [Endpoints](#endpoints)
  - [Creating an Account](#creating-an-account)
  - [Listing Accounts](#listing-accounts)
  - [Logging In](#logging-in)
  - [Registering a PGP Key](#registering-a-pgp-key)
  - [Responding to a Challenge](#responding-to-a-challenge)

## Features

- **Account Creation:** Create user accounts with a unique account ID and password.
- **Login:** Authenticate users with their account ID and password.
- **List Accounts:** Retrieve a list of registered accounts.
- **Key Registration:** Register PGP keys associated with user accounts.
- **PGP Key Signing:** Sign registered PGP keys for users.

## Installation
Prerequisites
Python3
nginx
Flask
gnupg
PGPy
A functioning SMTP server

Install Dependencies
sudo apt update
sudo apt install python3
sudo apt install python3-pip
sudo apt install python3-venv




Run the following command to install the required Python libraries:
## Install Python dependencies
pip install flask flask_cors gnupg PGPy


## Running the Application

python3 -m venv App
source App/bin/activate
python app.py


## Usage
## Endpoints
The application exposes several RESTful endpoints:

POST /create: Create a new user account.
GET /list: Retrieve a list of all user accounts.
POST /login: Log in to an existing user account.
POST /register: Register a PGP key for an account and sign a key

## Creating an Account
To create an account, make a POST request to /create with a JSON payload containing account-id and password

## Listing Accounts
Send a GET request to /list to get a list of all accounts.

## Logging In
To log in, make a POST request to /login with account-id and password.

## Registering a PGP Key
For PGP key registration, send a POST request to /register with account-id, password, email-address, key-id, and the PGP key file.

