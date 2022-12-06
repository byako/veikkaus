#!/bin/bash
docker run --rm -d -p 8080:80 -v /home/$USER/git/veikkaus/:/usr/share/nginx --name "lotto" nginx:latest
