#!/usr/bin/env bash

# Print usage
usage()
{
    echo "usage: liveMonitor.sh [-f] | [-m] | [-h]"
}

####################################################################
# Upload to live website
upload()
{
  # Is this a fireball
  if [ "$fireballs_only" = true ]
  then
    fr_file=`echo $ffname | sed 's/FF/FR/' | sed 's/fits/bin/'`
    if [ -f "$capdir/$fr_file" ]; then
      logger "This is a fireball $capdir/$fr_file" -t $0
      ~/ukmon/liveUploader.sh $capdir/$ffname
    fi

  # Is this a meteor and not a fireball
  elif [ "$meteors_only" = true ]
  then
    fr_file=`echo $ffname | sed 's/FF/FR/' | sed 's/fits/bin/'`
    if [ ! -f "$capdir/$fr_file" ]; then
      logger "This meteor is not a fireball" -t $0
      ~/ukmon/liveUploader.sh $capdir/$ffname
    fi

  # Upload whether fireball or not
  else
    ~/ukmon/liveUploader.sh $capdir/$ffname
  fi

}
####################################################################

# Check command line options
while [ "$1" != "" ]; do
    case $1 in
        -f | --fireball )       fireballs_only=true
                                ;;
        -m | --meteor )         meteors_only=true
                                ;;
        -h | --help )           usage
                                exit
                                ;;
        * )                     usage
                                exit 1
    esac
    shift
done


# Log options settings
if [ "$fireballs_only" = true ]
then
  logger "Monitoring for fireballs only" -t $0
fi
if [ "$meteors_only" = true ]
then
  logger "Monitoring for meteors only" -t $0
fi

# Outermost loop to monitor the RMS log(s) for detections
while [ 1 ]
do
  logf=`ls -1tr ~/RMS_data/logs/log*.log | tail -1 | head -1`
  capdir=""
  logger "Monitoring $logf" -t $0
  echo "Monitoring $logf"

  # Check for no log file
  if [ -z "$logf" ]
  then
    logger "No RMS log file found" -t $0
    sleep 300
  fi

  nice tail -Fn0 $logf | \
  while read -t 300 line ; do
    echo "$line" | grep "meteors:"| egrep -v ": 0"
    if [ $? = 0 ]
    then
      ffname=`echo "$line" | grep "meteors:"| egrep -v ": 0"| awk '{print $4}'`

      # Set the capture directory if if has not been set
      if [ -z "$capdir" ]
      then
        capdir=`grep "Data directory" $logf | awk '{print $6}'`
        logger "Setting capture directory to " $capdir -t $0
      fi

      echo   "found a meteor $ffname ..."
      logger "found a meteor $capdir/$ffname ..." -t $0

      # Upload to live website
      upload
    fi
  done

# Timeout on reading log file, so loop back to start
done
