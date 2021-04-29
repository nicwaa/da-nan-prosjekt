FROM httpd:alpine

COPY ./webUI.cgi /usr/local/apache2/cgi-bin/
COPY ./my-httpd.conf /usr/local/apache2/conf/httpd.conf

RUN apk update && apk upgrade && \
	apk add bash \
	curl \
	xmlstarlet \
	openssl \
	sqlite && \ 
	chmod 755 /usr/local/apache2/cgi-bin/webUI.cgi

EXPOSE 80

#ENTRYPOINT ["/bin/ash"]
#CMD apachectl restart
