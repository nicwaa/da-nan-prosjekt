#!/bin/bash

sudo docker run -t -d --network=myNetwork \
	--name webui_cont \
	-p 8080:80 \
	--rm \
	--cpuset-cpus 0 \
	--cpu-shares 256 \
	--cap-drop CHOWN \
	webui
