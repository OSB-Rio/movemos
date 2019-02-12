#!/bin/bash

FOLDER="/root/movemos"
FOLDER_TO_COMPRESS=$(date --date="1 day ago" +%Y%m%d)
FILE=$(date --date="1 day ago" +%Y%m%d)".tar.gz"

cd $FOLDER/backups

tar cz $FOLDER_TO_COMPRESS -f $FILE
