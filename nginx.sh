#!/bin/bash
docker run --restart unless-stopped -d -p 8080:80 -v /home/$USER/git/veikkaus/:/usr/share/nginx --name "lotto" nginx:latest
