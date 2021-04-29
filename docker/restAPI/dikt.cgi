#!/bin/bash

read BODY

my_namespace="http://localhost/"
db_path="/usr/local/apache2/Database/test.db"

# Skriver ut 'http-header' for 'plain-text'
echo "Content-type:text/xml;charset=utf-8"
echo "Access-Control-Allow-Origin: http://localhost"
echo "Access-Control-Allow-Credentials: true"
echo "Access-Control-Allow-Methods: POST,PUT,DELETE,GET"

# Skriver ut tom linje for å skille hodet fra kroppen
echo

if [ $REQUEST_URI ]; then
element=$(echo $REQUEST_URI | cut -d/ -f3)
fi
if [ $HTTP_COOKIE ]; then
sessionID=$(echo $HTTP_COOKIE | cut -d= -f2)
fi
if [ $sessionID ]; then
valid_session=$(sqlite3 /usr/local/apache2/Database/test.db \
                "select * from sesjon where sesjonsID='$sessionID';")
fi

if [ $valid_session ];then
    my_epost=$(echo $valid_session | cut -f2 -d\|)
    my_session=$(echo $valid_session | cut -f1 -d\|)
fi

req=$REQUEST_METHOD

if [ $req = 'GET' ]; then
	if [ -z $element ]; then
		alle_dikt=$(echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
		#alle_dikt=$alle_dikt$(echo "<?xml-stylesheet type=\"text/xsl\" href=\"http://localhost/xml_style.xsl\"?>")
		alle_dikt=$alle_dikt$(echo "<alle_dikt xmlns=\"$my_namespace\" \
        xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" \
        xsi:schemaLocation=\"$my_namespace xml_schema.xsd\">")
		temp=$(sqlite3 $db_path "SELECT diktID,dikt FROM Dikt;")
		oldIFS=$IFS
		IFS=$'\n'
		for p in $temp;
		do
			alle_dikt=$alle_dikt$(echo "<dikt>")
			alle_dikt=$alle_dikt$(echo "<id>$(echo $p | cut -f1 -d\|)</id>")
			alle_dikt=$alle_dikt$(echo "<tekst>$(echo $p | cut -f2 -d\|)</tekst>")
			alle_dikt=$alle_dikt$(echo "</dikt>")
		done
		IFS=$oldIFS
		alle_dikt=$alle_dikt$(echo "</alle_dikt>")
		echo "$alle_dikt"
		unset alle_dikt
	else
		dikt=$(echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
		#dikt=$dikt$(echo "<?xml-stylesheet type=\"text/xsl\" href=\"http://localhost/xml_style_1_dikt.xsl\"?>")
		dikt=$dikt$(echo "<dikt xmlns=\"$my_namespace\" \
        xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" \
        xsi:schemaLocation=\"$my_namespace xml_schema.xsd\">")
		temp=$(sqlite3 $db_path \
					"SELECT diktID,dikt FROM Dikt where diktID=$element;")
		dikt=$dikt$(echo "<id>$(echo "$temp" | cut -f1 -d\|) </id>")
		dikt=$dikt$(echo "<tekst>$(echo "$temp" | cut -f2 -d\|)</tekst>")
		dikt=$dikt$(echo "</dikt>")
		echo "$dikt"
		unset dikt
	fi
elif [ $req = 'POST' ] && [ $valid_session ]; then
	#echo POST_STUFF 
	dikt_tekst=$(echo $BODY | xmlstarlet sel -N ns="http://localhost/" -t -v "ns:api/ns:dikt/ns:tekst")
	sqlite3 $db_path \
			"INSERT INTO dikt(dikt, email) VALUES('$dikt_tekst', '$my_epost');"
	check_insert=$(sqlite3 $db_path \
					"SELECT dikt FROM dikt WHERE dikt='$dikt_tekst';")
	if [ "$check_insert" ]; then
		echo nice
	else
		echo dum
	fi
elif [ $req = 'PUT' ] && [ $valid_session ] && [ $element ]; then
	#echo PUT_STUFF
	endre_dikt_tekst=$(echo $BODY | xmlstarlet sel -N ns="http://localhost/" -t -v "ns:api/ns:dikt/ns:tekst")
	sqlite3 $db_path \
			"UPDATE dikt SET dikt='$endre_dikt_tekst' \
			WHERE diktID=$element AND email='$my_epost';"
	check_update=$(sqlite3 $db_path \
					"SELECT dikt FROM dikt WHERE diktID=$element;")
	if [ "$check_update" = "$endre_dikt_tekst" ]; then
		echo nice
	else
		echo dum
	fi
elif [ $req = 'DELETE' ] && [ $valid_session ]; then
	#echo DELETE_STUFF
	if [ -z $element ]; then
		sqlite3 $db_path \
				"DELETE FROM Dikt WHERE email='$my_epost';"
	else
		sqlite3 $db_path \
				"DELETE FROM Dikt WHERE diktID=$element AND email='$my_epost';"
	fi
	check_delete=$(sqlite3 $db_path \
					"SELECT * FROM DIKT WHERE diktID=$objekt AND email='$my_epost';")
	if [ -z $check_delete ]; then
		echo nice
	else
		echo dum
	fi
else
	echo dum_dum
fi
