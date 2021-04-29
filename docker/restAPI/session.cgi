#!/bin/bash

# Skriver ut 'http-header' for 'plain-text'
echo "Content-type:text/plain;charset=utf-8"
echo "Access-Control-Allow-Origin: http://localhost"
echo "Access-Control-Allow-Credentials: true"
echo


sessionID=$(echo $HTTP_COOKIE | cut -d= -f2)
action=$(echo $REQUEST_URI | cut -d/ -f3)

if [ $sessionID ] && [ $REQUEST_METHOD = "GET" ] && [ $action = "fetch" ]; then
    checkSession=$(sqlite3 /usr/local/apache2/Database/test.db \
                "select * from sesjon where sesjonsID='$sessionID';")
fi
#echo $element
echo "$checkSession"
