#!/bin/bash

grim -g "$(slurp)" $(xdg-user-dir PICTURES)/$(date +'%s_screenshot.png') | wl-copy -t "image/png"
#grim -g "$(slurp)" $(xdg-user-dir PICTURES)/$(date +'%s_grim.png')
