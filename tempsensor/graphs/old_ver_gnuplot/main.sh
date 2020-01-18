#!/bin/bash
TPATH="/home/aorith/tempsensor/graphs/pg"
cd "$TPATH" || return
today=$(date +"%Y%m%d")
yesterday=$(date -d 'yesterday' +"%Y%m%d")
current_hour=$(date +"%H")
avg=$($TPATH/../scr/t_avg.sh)
avg_today=$($TPATH/../scr/t_avg_daily.sh "$today" "$current_hour" | cut -d',' -f2)
avg_yesterday=$($TPATH/../scr/t_avg_daily.sh "$yesterday" "$current_hour" | cut -d',' -f2)
difference=$(echo "scale=2; ($avg_today - $avg_yesterday)" | bc)

$TPATH/all.pg
$TPATH/cpu.pg
$TPATH/cpu_today.pg
$TPATH/today_vs_yesterday.pg

HTML_FILE="$TPATH/../www/data.php"
true> $HTML_FILE
echo "<div align='center'><h3>Temp and humidity graphs</h3></div><div id='data'>" >> $HTML_FILE
echo "<table id='datatable'>" >> $HTML_FILE
echo "<tr><td>full data average: </td><td>$avg</td></tr>" >> $HTML_FILE
echo "<tr><td>today's average:</td><td>$avg_today</td></tr>" >> $HTML_FILE
echo "<tr><td>yesterday's average: </td><td>$avg_yesterday</td></td></tr>" >> $HTML_FILE
echo "<tr><td>difference:</td><td>$difference</td></tr>" >> $HTML_FILE
echo "</table></div>" >> $HTML_FILE

#for i in /var/www/html/*.svg; do echo "<p><img src='$(basename $i)' /></p>"; done >> /home/aorith/tempsensor/graphs/www/temp

cp $TPATH/../www/* /var/www/html/temp/
