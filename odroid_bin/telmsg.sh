#!/bin/bash

TEXT="$*"
TOKEN="$(sed -n 1p /home/aorith/secret/api-telbot.txt)"
CHATID="$(sed -n 2p /home/aorith/secret/api-telbot.txt)"
TIME="10"
URL="https://api.telegram.org/bot$TOKEN/sendMessage"

# send message
curl -s --max-time $TIME -d "chat_id=$CHATID&disable_web_page_preview=1&text=$TEXT" "$URL" >/dev/null

# receive messages
#URL_UPDATES="https://api.telegram.org/bot$TOKEN/getUpdates"
#curl -s --max-time $TIME $URL_UPDATES
