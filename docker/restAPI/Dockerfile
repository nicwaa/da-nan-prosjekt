FROM httpd:alpine

COPY ./test.db /usr/local/apache2/Database/
COPY ./my-httpd.conf /usr/local/apache2/conf/httpd.conf
COPY ./dikt.cgi /usr/local/apache2/cgi-bin
COPY ./login.cgi /usr/local/apache2/cgi-bin
COPY ./session.cgi /usr/local/apache2/cgi-bin

RUN apk update && apk upgrade && \
	apk add bash \
	curl \
	xmlstarlet \
	openssl \
	sqlite && \ 
	chmod 755 /usr/local/apache2/cgi-bin/dikt.cgi && \
	chmod 755 /usr/local/apache2/cgi-bin/login.cgi && \
	chmod 755 /usr/local/apache2/cgi-bin/session.cgi && \
	chmod 777 -R /usr/local/apache2/Database

EXPOSE 80
