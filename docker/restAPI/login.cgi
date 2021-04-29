#!/bin/bash

# Skriver ut 'http-header' for 'plain-text'
echo "Content-type:text/plain;charset=utf-8"
echo "Access-Control-Allow-Origin: http://localhost"
echo "Access-Control-Allow-Credentials: true"
echo "Access-Control-Allow-Methods: POST,DELETE"

# Skriver ut tom linje for å skille hodet fra kroppen
echo

db_path="/usr/local/apache2/Database/test.db"

read BODY

login=$(echo $BODY | xmlstarlet sel -N ns="http://localhost/" -t -m ns:bruker -v ns:email)
password_unhashed=$(echo $BODY | xmlstarlet sel -N ns="http://localhost/" -t -m ns:bruker -v ns:passord)

if [ $password_unhashed ]; then
password=$(openssl passwd -6 -salt xyz $password_unhashed)
fi

session_id=$(echo $HTTP_COOKIE | cut -d= -f2)
action=$(echo $REQUEST_URI | cut -d/ -f3)
valid_session=$(sqlite3 /usr/local/apache2/Database/test.db \
                "select * from sesjon where sesjonsID='$session_id';")

#echo $BODY
#echo $login
#echo $password
#echo $snx

if [ $REQUEST_METHOD = 'POST' ]; then

    if [ $login ] && [ $password ]; then    
        pw_hash=$(sqlite3 $db_path \
            "select passordhash from bruker where email='$login';")
    
        if [ $password = $pw_hash ]; then
            dato=$(date '+%d/%m/%Y_%H:%M:%S')
            sessionID=$(openssl passwd -6 $dato$pw_hash | cut -d$ -f4)
            sqlite3 $db_path \
                "INSERT INTO Sesjon (sesjonsID, email) VALUES (\"$sessionID\", \"$login\");"
            echo $sessionID
        fi
    fi
elif [ $REQUEST_METHOD = 'DELETE' ] && [ $valid_session ] && [ $action = "logout" ]; then
    
    if [ $session_id ]; then
        sqlite3 $db_path \
            "DELETE FROM Sesjon WHERE sesjonsID='$session_id';"
    fi
else
    echo $valid_session
fi
