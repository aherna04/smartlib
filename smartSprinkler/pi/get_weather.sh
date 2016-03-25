#!/bin/bash

if [ $# != 2 ]; then
        echo " How to use:"
        echo " get_weather.sh <zip or localweather code> <airport code>"
        echo
        echo " Lookup airport codes here:"
        echo " http://forecast.weather.gov/zipcity.php"
        echo
        echo " examples: get_weather.sh USFL0559 KPMP"
        echo "           get_weather.sh 33322 KFLL"

        exit
fi

#### My vars
nanotime=`date +'%s'`
mydate=`date`
currentWind=0
currentHumidity=0
sunrise=0
sunset=0
codeToday=0
codeTomorrow=0
lowestTemp=0
lowToday=0
highestTemp=0
rainChanceToday=0
windToday=0
avgWinds=0
aveRainChance=0
accumulatedRain=0

weekSkipThreshold=2.5
daySeconds=86400
weekSkip=604800


#### figure out if we need curl or wget ####
myuname=`uname`
if [[ $myuname == 'Linux'  ]]; then
   webscript="curl --stderr /dev/null --basic --url"
elif [[ $myuname == 'Darwin'  ]]; then
   webscript="curl --stderr /dev/null --basic --url"
else // this is good enough for now.  
   webscript="wget -q -O- "
fi
 
#### deal with the shell params 
station=$1
airportcode=$2

#### temp files 
mytempweather=/home/pi/tmp/weather.out
mytempyahoo=/home/pi/tmp/yweather.out
mytempyahoo2=/home/pi/tmp/yweather2.out
mytempyahoo3=/home/pi/tmp/yweather3.out

check_skip_week ()
{
   #Check for skipper file... 
   if [[ -f week.skip ]]; then 
	   echo "***Still in skip window***"
   
   else
	if [[ $accumulatedRain > $weekSkipThreshold  ]]; then
	   echo "***Too much rain, skipping for 1 week***"
	   touch week.skip
	   echo `expr $nanotime + $weekSkip` > week.skip
	fi   
   fi	
   
}

generate_files ()
{
   $webscript "http://weather.yahooapis.com/forecastrss?p=$station" > $mytempyahoo
   $webscript "http://www.weather.com/weather/5-day/$station" > $mytempweather
}

print_header ()
{
   echo $mydate
   cat $mytempyahoo | awk 'BEGIN{FS="<title>";}{print $2}' | grep Conditions | cut -d"<" -f1

   #current Conditions
   $webscript "http://xml.weather.yahoo.com/forecastrss?p=$station&u=f" | grep -E '(Current Conditions:|F<BR)' | sed -e 's/Current Conditions://' -e 's/<br \/>//' -e 's/<b>//' -e 's/<\/b>//' -e 's/<BR \/>//' -e 's///' -e 's/<\/description>//'
   echo "-----------------------------------"
}

cleanup ()
{
   rm $mytempweather
   rm $mytempyahoo
   rm $mytempyahoo2
}

parse_yahoo ()
{
	#Yahoo API# - I prefer this better than yahoo XML, butt does not provide %chance of rain, etc
	#use weather.com for rain and wind

	#1st parse of yahoo RSS Feed - find the fields
	cat $mytempyahoo | awk 'BEGIN{RS="yweather:" } {print "RECORD: " $0}' | grep RECORD | egrep -e location -e wind -e atmosphere -e astronomy -e code | cut -d" " -f2- | cut -d"/" -f1 > $mytempyahoo2

	#2nd pass of yahoo RSS Feed - print the sunrise/sunset, humidity, and current winds
	 #the wind will be used to skip sprinkler cycle if too windy
	 #the sunset and sunrise times can be used to set schedule markers... sunset+4 hrs, etc
	cat $mytempyahoo2 | cut -d" " -f2- | sed -e 's/"\ /"\n/g' -e 's/^ *//g' -e 's/\"//g'| awk 'BEGIN{FS="=";OFS="|";}{print $1,$2}' | grep  -v day | grep -v ^\| | grep -v date | grep -v text | sed 's/^ *//g' | grep -e sun -e humi -e speed

	currentWind=`cat $mytempyahoo2 | cut -d" " -f2- | sed -e 's/"\ /"\n/g' -e 's/^ *//g' -e 's/\"//g'| awk 'BEGIN{FS="=";OFS="|";}{print $1,$2}' | grep  -v day | grep -v ^\| | grep -v date | grep -v text | sed 's/^ *//g' | grep -e speed | cut -d"|" -f2`
	currentHumidity=`cat $mytempyahoo2 | cut -d" " -f2- | sed -e 's/"\ /"\n/g' -e 's/^ *//g' -e 's/\"//g'| awk 'BEGIN{FS="=";OFS="|";}{print $1,$2}' | grep  -v day | grep -v ^\| | grep -v date | grep -v text | sed 's/^ *//g' | grep -e humi | cut -d"|" -f2`
	sunrise=`cat $mytempyahoo2 | cut -d" " -f2- | sed -e 's/"\ /"\n/g' -e 's/^ *//g' -e 's/\"//g'| awk 'BEGIN{FS="=";OFS="|";}{print $1,$2}' | grep  -v day | grep -v ^\| | grep -v date | grep -v text | sed 's/^ *//g' | grep -e sunrise | cut -d"|" -f2`
	sunset=`cat $mytempyahoo2 | cut -d" " -f2- | sed -e 's/"\ /"\n/g' -e 's/^ *//g' -e 's/\"//g'| awk 'BEGIN{FS="=";OFS="|";}{print $1,$2}' | grep  -v day | grep -v ^\| | grep -v date | grep -v text | sed 's/^ *//g' | grep -e sunset | cut -d"|" -f2`


	#filter the high, low, and weather codes
	cat $mytempyahoo2 | cut -d" " -f5- | grep text | sed -e 's/"\ /\
/g'  -e 's/^ *//g' -e 's/\"//g' -e 's/\"//g'| awk 'BEGIN{FS="=";OFS=":";}{print $1,$2}' | grep  -v "day" | grep -v ^\: | grep -v "date" > $mytempyahoo3

	codeToday=`cat $mytempyahoo3 | grep code | head -1 | cut -d":" -f2`
	codeTomorrow=`cat $mytempyahoo3 | grep code | head -2 | tail -1 | cut -d":" -f2`
	lowToday=`cat $mytempyahoo3 | grep low | head -1 | cut -d":" -f2`

	echo "-----------------------------------"
	cat $mytempyahoo3 | grep -e low 
	echo "-----------------------------------"
	cat $mytempyahoo3 | grep -e high 
	echo "-----------------------------------"
	cat $mytempyahoo3 | grep -e code 
	echo "-----------------------------------"
	cat $mytempyahoo3 | grep -e text 
	echo "-----------------------------------"

	#find the high and lows for the week. The low will be used incase we need to skip for a freeze
	lowestTemp=`cat $mytempyahoo3 | grep -e low | cut -d":" -f2- | awk 'NR == 1 {max=$1 ; min=$1} $1 >= max {max = $1} $1 <= min {min = $1} END { print min }'`
	echo "Low for the week: $lowestTemp"

	highestTemp=`cat $mytempyahoo3 | grep -e high | cut -d":" -f2- | awk 'NR == 1 {max=$1 ; min=$1} $1 >= max {max = $1} $1 <= min {min = $1} END { print max }'`
	echo "High for the week: $highestTemp"

	# yahoo XML for 33071
	echo "-----------------------------------"
	echo "Yahoo xml"
}

parse_weather_com ()
{
	echo "Rain chance for the week"
	cat $mytempweather | awk 'BEGIN{RS="<title>" } {print "RECORD: " $0}' | grep -v class | grep  "%" | cut -d">" -f2| cut -d"<" -f1
	avgRainChance=`cat $mytempweather | awk 'BEGIN{RS="<title>" } {print "RECORD: " $0}' | grep -v class | grep  "%" | cut -d">" -f2| cut -d"<" -f1 | cut -d"%" -f1 | awk '{sum+=$1} END {print (sum+0)/NR } '`
	rainChanceToday=`cat $mytempweather | awk 'BEGIN{RS="<title>" } {print "RECORD: " $0}' | grep -v class | grep  "%" | cut -d">" -f2| cut -d"<" -f1 | cut -d"%" -f1 | head -1`
	rainChanceTomorrow=`cat $mytempweather | awk 'BEGIN{RS="<title>" } {print "RECORD: " $0}' | grep -v class | grep  "%" | cut -d">" -f2| cut -d"<" -f1 | cut -d"%" -f1 | head -2 | tail -1`
	rainChanceAfterTomorrow=`cat $mytempweather | awk 'BEGIN{RS="<title>" } {print "RECORD: " $0}' | grep -v class | grep  "%" | cut -d">" -f2| cut -d"<" -f1 | cut -d"%" -f1 | head -3 | tail -1`

	echo "-----------------------------------"
	echo "Rain chance for today: $rainChanceToday%"
	echo "-----------------------------------"

	#winds for today
	windToday=`cat $mytempweather | awk 'BEGIN{RS="<title>" } {print "RECORD: " $0}' | grep -v class | grep  "mph" | cut -d" " -f3  | head -1`
	echo "Winds for today: $windToday"

	echo "Winds for the next week"
	cat $mytempweather | awk 'BEGIN{RS="<title>" } {print "RECORD: " $0}' | grep -v class | grep  "mph" | cut -d" " -f3  
	echo "-----------------------------------"
	#average winds
	avgWinds=`cat $mytempweather | awk 'BEGIN{RS="<title>" } {print "RECORD: " $0}' | grep -v class | grep  "mph" | cut -d" " -f3  | awk '{sum+=$1} END {print (sum+0)/NR }'`
	echo "Average winds for the week: $avgWinds"
	echo "Average rain for the week: $avgRainChance%" 
}

get_rain ()
{
	# Rain totals
	echo "-----------------------------------"
	#####get_rainHistory.sh $airportcode

	accumulatedRain=`$webscript http://w1.weather.gov/data/obhistory/$airportcode.html | awk 'BEGIN{FS="</td>";OFS=":";}{print  $8 }'| sed -e s/"<td>"//g | more | grep -v ":::" | grep "\." | awk '{sum+=$1} END {print sum+0 } '`
	echo "Rain in the last 72 hrs for $airportcode: $accumulatedRain"
}

#now that it's parsed, we can easily dump it into a DB, etc

### main ###
generate_files
 print_header
  parse_yahoo
  parse_weather_com
 get_rain
 check_skip_week
cleanup

#########################################################

touch /home/pi/weathertest/logs/$nanotime.log

echo
echo "nanotime:$nanotime" >>/home/pi/weathertest/logs/$nanotime.log
echo "mydate:$mydate" >>/home/pi/weathertest/logs/$nanotime.log
echo "currentWind:$currentWind" >>/home/pi/weathertest/logs/$nanotime.log
echo "currentHumidity:$currentHumidity" >>/home/pi/weathertest/logs/$nanotime.log
echo "sunrise:$sunrise" >>/home/pi/weathertest/logs/$nanotime.log
echo "sunset:$sunset" >>/home/pi/weathertest/logs/$nanotime.log
echo "lowToday:$lowToday" >>/home/pi/weathertest/logs/$nanotime.log
echo "codeToday:$codeToday" >>/home/pi/weathertest/logs/$nanotime.log
echo "codeTomorrow:$codeTomorrow" >>/home/pi/weathertest/logs/$nanotime.log
echo "lowestTemp:$lowestTemp" >>/home/pi/weathertest/logs/$nanotime.log
echo "highestTemp:$highestTemp" >>/home/pi/weathertest/logs/$nanotime.log
echo "rainChanceToday:$rainChanceToday" >>/home/pi/weathertest/logs/$nanotime.log
echo "rainChanceTomorrow:$rainChanceTomorrow" >>/home/pi/weathertest/logs/$nanotime.log
echo "rainChanceAfterTomorrow:$rainChanceAfterTomorrow" >>/home/pi/weathertest/logs/$nanotime.log
echo "windToday:$windToday" >>/home/pi/weathertest/logs/$nanotime.log
echo "avgWinds:$avgWinds" >>/home/pi/weathertest/logs/$nanotime.log
echo "avgRainChance:$avgRainChance" >>/home/pi/weathertest/logs/$nanotime.log
echo "accumulatedRain:$accumulatedRain" >>/home/pi/weathertest/logs/$nanotime.log




#echo
#echo "nanotime                      |$nanotime" >>logs/$nanotime.log
#echo "date                          |$mydate" >>logs/$nanotime.log
#echo "current winds                 |$currentWind" >>logs/$nanotime.log
#echo "current humidity              |$currentHumidity" >>logs/$nanotime.log
#echo "sunrise                       |$sunrise" >>logs/$nanotime.log
#echo "sunset                        |$sunset" >>logs/$nanotime.log
#echo "low Today                     |$lowToday" >>logs/$nanotime.log
#echo "code today                    |$codeToday" >>logs/$nanotime.log
#echo "code tomorrow                 |$codeTomorrow" >>logs/$nanotime.log
#echo "lowest temp for the week      |$lowestTemp" >>logs/$nanotime.log
#echo "highest temp for the week     |$highestTemp" >>logs/$nanotime.log
#echo "rain chance for today         |$rainChanceToday" >>logs/$nanotime.log
#echo "rain chance for tomorrow      |$rainChanceTomorrow" >>logs/$nanotime.log
#echo "rain chance for after tomrrow |$rainChanceAfterTomorrow" >>logs/$nanotime.log
#echo "winds for today               |$windToday" >>logs/$nanotime.log
#echo "avg winds for the week        |$avgWinds" >>logs/$nanotime.log
#echo "avg rain for the week         |$avgRainChance" >>logs/$nanotime.log
#echo "total rain in last 72 hours   |$accumulatedRain" >>logs/$nanotime.log

cat /home/pi/weathertest/logs/$nanotime.log
exit


##NOTES
Type:
manual test, run for 3 seconds, exit

Type:
Scheduled cycle

if it rained 2 inches in 72 hours, skip a week. 

If it rained .5 inches in the last 72 hours, skip cycle

if there is a >50% chance of rain within 48 hours, skip cycle
  if there is a >80% in 72 hrs, exit

if the current wind is 20mph or higher, postpone cycle 24 hrs, skip cycle

if the lowToday is < 34, postpone cycle 24 hrs, skip cycle

if there is a freeze expected, postpone cycle, skip cycle

else, run as scheduled.



