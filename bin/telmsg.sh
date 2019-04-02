#!/bin/bash

TEXT="$@"
TOKEN="$(cat /home/aorith/secret/api-telbot.txt)"
CHATID="5193892"
TIME="10"
URL_UPDATES="https://api.telegram.org/bot$TOKEN/getUpdates"
URL="https://api.telegram.org/bot$TOKEN/sendMessage"

# send message
curl -s --max-time $TIME -d "chat_id=$CHATID&disable_web_page_preview=1&text=$TEXT" $URL >/dev/null

# receive messages
#curl -s --max-time $TIME $URL_UPDATES
