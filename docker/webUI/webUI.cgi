#!/bin/bash

read BODY

base_url="rest_api_cont/"
my_namespace="http://localhost/"

if [ $HTTP_COOKIE ]; then
    sessionCheck=$(curl -H "Cookie: $HTTP_COOKIE" $base_url"session/fetch")
    if [ $sessionCheck ];then
        my_epost=$(echo $sessionCheck | cut -f2 -d\|)
        my_session=$(echo $sessionCheck | cut -f1 -d\|)
    fi
fi

if [ $sessionCheck ] && [ $BODY = "action=logout" ]; then
    curl -H "Cookie: $HTTP_COOKIE" -X DELETE $base_url"login/logout"
    sessionCheck=$(curl -H "Cookie: $HTTP_COOKIE" $base_url"session/fetch")

elif [ $QUERY_STRING = "action=hent+alle+dikt" ]; then
    alle_dikt=$(curl $base_url"dikt/")
    gi_meg=1

elif [ $(echo $QUERY_STRING | cut -f1 -d=) = "diktID" ]; then
    id_verdi=$(echo $QUERY_STRING | cut -f2 -d=)
    dikt=$(curl $base_url"dikt/$id_verdi")
    gi_meg=2

elif [ $sessionCheck ] && [ $(echo $BODY | cut -f1 -d=) = "lagre_nytt_dikt" ]; then
    
    fix_nytt_dikt=$(echo $BODY | sed s/+/' '/g | sed s/%2C/,/g)
    fix_nytt_dikt=$(echo $fix_nytt_dikt | cut -f2 -d=)
    
    post_nytt_dikt=$(echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
    post_nytt_dikt=$post_nytt_dikt$(echo "<api xmlns=\"$my_namespace\" \
        xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" \
        xsi:schemaLocation=\"$my_namespace xml_schema.xsd\">")
    post_nytt_dikt=$post_nytt_dikt$(echo \
        "<dikt><tekst>$fix_nytt_dikt</tekst></dikt></api>")
    
    check_insert=$(curl -d "$post_nytt_dikt" -H "Cookie: $HTTP_COOKIE" \
        -X POST $base_url"dikt/")

elif [ $sessionCheck ] && [ $(echo $BODY | cut -f1 -d=) = "endre_dikt_id" ] && \
        [ $(echo $BODY | cut -f2 -d\& | cut -f1 -d=) = "endre_dikt" ]; then
    
    endre_dikt_id=$(echo $BODY | cut -f1 -d\& | cut -f2 -d=)
    endre_dikt_tekst=$(echo $BODY | cut -f2 -d\& | cut -f2 -d=)
    
    endre_dikt_tekst=$(echo $endre_dikt_tekst | sed s/+/' '/g | sed s/%2C/,/g)
    endre_dikt=$(echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
    
    endre_dikt=$endre_dikt$(echo "<api xmlns=\"$my_namespace\" \
        xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" \
        xsi:schemaLocation=\"$my_namespace xml_schema.xsd\">")
    endre_dikt=$endre_dikt$(echo "<dikt><tekst>$endre_dikt_tekst</tekst>\
        <epost>$my_epost</epost></dikt></api>")
    
    check_update=$(curl -d "$endre_dikt" -H "Cookie: $HTTP_COOKIE"\
         -X PUT $base_url"dikt/$endre_dikt_id")

elif [ $sessionCheck ] && [ $(echo $BODY | cut -f1 -d=) = "slett_dikt_id" ]; then
    slett_dikt_id=$(echo $BODY | cut -f2 -d=)
    check_delete=$(curl -H "Cookie: $HTTP_COOKIE" -X DELETE $base_url"dikt/$slett_dikt_id")

elif [ $sessionCheck ] && [ $(echo $BODY | cut -f2 -d=) = "Slett+alle+egne+dikt" ]; then
    check_delete_all=$(curl -H "Cookie: $HTTP_COOKIE" -X DELETE $base_url"dikt/")

elif [ -z $sessionCheck ] && [ $BODY ]; then
    
    # Fikser spesialtegnet '@' i $BODY
    fix=$(echo $BODY | sed s/%40/@/g)
    # Klipper ut epost
    epost=$(echo $fix | cut -f1 -d\& | cut -f2 -d=)
    # Klipper ut passord
    pw=$(echo $fix | cut -f2 -d\& | cut -f2 -d=)
    
    # Xml-formatterer epost og passord
    login_temp=$(echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
    login_temp=$login_temp$(echo "<bruker xmlns=\"$my_namespace\" \
        xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" \
        xsi:schemaLocation=\"$my_namespace xml_schema.xsd\">")
    login_temp=$login_temp$(echo "<email>$epost</email> \
            <passord>$pw</passord></bruker>")
    
    # Sender xml-fil til API for å undersøke oppgitt legitimasjon
    conc_my_cat="login/"
    sessionID=$(curl -d "$login_temp" -H "Content-Type: application/xml"\
                 -X POST $base_url$conc_my_cat)
    
    # Dersom API-et mottar gyldig legitimasjon sender det tilbake en sesjons-ID
    if [ $sessionID ]; then
        # Forer sesjons-ID til nettleseren
        echo "Set-Cookie:SessionID=$sessionID;Max-Age=600;SameSite=Lax"
    fi
fi


if [ $sessionCheck ] || [ $sessionID ]; then
    # Dette betyr at sesjonen fantes eller at login var vellykket
    # Fullverdig html-skjema kan dermed presenteres direkte
    if [ $gi_meg -eq 1 ]; then
        echo "Content-Type:text/xml;charset=utf-8"
        echo

        echo $alle_dikt
        #unset alle_dikt
        unset gi_meg
        #echo something
    elif [ $gi_meg -eq 2 ]; then
        echo "Content-Type:text/xml;charset=utf-8"
        echo

        echo $dikt
        unset dikt
        unset gi_meg
    else
        echo "Content-type:text/html;charset=utf-8"
        echo

        cat << EOF
        <!doctype html>
        <html>
            <head>
                <link href="http://localhost/stiler.css" rel="stylesheet" type="text/css" />
                <meta charset='utf-8'>
                <title>WebUI</title>
            </head>
            <body>
                <div>
                    <h2><a href="http://localhost/index.html">Hjemmeside</a></h2>
                    <h1>Du er innlogget :-)</h1>
                    <form method='post' accept-charset="utf-8">
                        <input type="submit" name=action value=logout>
                    </form><br><br><br>
                    <form action=/dikt accept-charset="utf-8">
                            <input type="submit" name=action value='hent alle dikt'>
                    </form><br>
                    <form action=/dikt accept-charset="utf-8">
                            <label for="diktID">diktID:</label><br>
                            <input type=number id=diktID name=diktID value='Angi diktID'><br>
                            <input type=submit value='Hent dikt'>
                    </form><br>
                    <form method='post' accept-charset="utf-8">
                        <label for='Post_dikt'>Skap et nytt dikt:</label><br>
                        <input type=text id='Post_dikt' name='lagre_nytt_dikt' value='Skriv inn ditt dikt her'><br>
                        <input type=submit value='Lagre dikt'><br>
                    </form>
                    Check insert: $check_insert <br><br>
                    <p>Revider eksisterende dikt:</p>
                    <form method='post' accept-charset="utf-8">
                        <label for='endre_dikt_id'>Dikt ID:</label><br>
                        <input type=number id='endre_dikt_id' name='endre_dikt_id'><br>
                        <label for='endre_dikt'>Endre dikt:</label><br>
                        <input type=text id='endre_dikt' name='endre_dikt'><br>
                        <input type=submit value='Endre dikt'><br>
                    </form>
                    Check update: $check_update <br><br>
                    <p>Slett dikt:</p>
                    <form method='post' accept-charset="utf-8">
                        <label for='slett_dikt_id'>Dikt ID:</label><br>
                        <input type=number id='slett_dikt_id' name='slett_dikt_id'><br>
                        <input type=submit value='Slett dikt'><br>
                    </form>
                    Check delete: $check_delete <br><br>
                    <form method='post' accept-charset="utf-8">
                        <input type="submit" name=action value="Slett alle egne dikt">
                    </form>
                    Check delete all: $check_delete_all
                </div>
            </body>
        </html>  
EOF
        echo "<h1>Feilsøking:</h1>"
        echo "QUERY_STRING: $QUERY_STRING <br>"
        echo "Fix: $fix <br>"
        echo "Body: $BODY <br>"
        echo "Epost: $epost <br>"
        echo "Password: $pw <br>"
        echo "SessionID: $sessionID <br>"
        echo "Fiks dikt: $fix_nytt_dikt <br>"
        echo "Dikt epost: $dikt_epost <br>"
        echo "post_nytt_dikt: $post_nytt_dikt <br>"
    fi
else

    if [ $gi_meg -eq 1 ]; then
        echo "Content-Type:text/xml;charset=utf-8"
        echo

        echo $alle_dikt
        unset alle_dikt
        unset gi_meg
        #echo something
    elif [ $gi_meg -eq 2 ]; then
        echo "Content-Type:text/xml;charset=utf-8"
        echo

        echo $dikt
        unset dikt
        unset gi_meg
    else
        # Ugyldig/ingen cookie ble oppgitt
        # Begrenset html-skjema med login-mulighet presenteres for bruker
        echo "Content-type:text/html;charset=utf-8"
        echo

        cat << EOF
        <!doctype html>
        <html>
            <head>
                <link href="http://localhost/stiler.css" rel="stylesheet" type="text/css" />
                <meta charset='utf-8'>
                <title>WebUI</title>
            </head>
            <body>
                <h2><a href="http://localhost/index.html">Hjemmeside</a></h2>
                <h1>Du er ikke innlogget :-(</h1>
                <form method='post' accept-charset="utf-8">
                    <label for="un">Epost:</label><br>
                    <input type=email id=un name=epost value='test@testen.no'><br>
                    <label for="pw">Passord:</label><br>
                    <input type=password id=pw name=passord value='2'><br>
                    <input type=submit value=login>
                </form><br><br><br>
                <form action=/dikt accept-charset="utf-8">
                    <input type="submit" name='action' value='hent alle dikt'><br>
                </form><br>
                <form action=/dikt accept-charset="utf-8">
                    <label for="diktID">diktID:</label><br>
                    <input type=number id=diktID name=diktID value='Angi diktID'><br>
                    <input type=submit value='Hent dikt'>
                </form><br>
            </body>
        </html>  
EOF

        echo "<h1>Feilsøking:</h1>"
        echo "QUERY_STRING: $QUERY_STRING <br>"
        echo "Fix: $fix <br>"
        echo "Fant ikke sesjon <br>"
        echo "Body: $BODY <br>"
        echo "Epost: $epost <br>"
        echo "Password: $pw <br>"
        echo "SessionID: $sessionID <br>"
    
    fi
fi
