#!/bin/bash

sudo docker run -t -d --network=myNetwork \
	--name rest_api_cont \
	--rm \
	-p 8181:80 \
	--cpuset-cpus 1 \
        --cpu-shares 256 \
	--cap-drop CHOWN \
	rest_api
