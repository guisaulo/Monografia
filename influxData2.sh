#!/bin/bash

sort -k 3 | awk NF | uniq -c | sed -e "s/value=/value\ /" | awk '{ printf("%s value=%s %s\n", $2, $1*$4*10, $5 ) }' | sort -k 3
