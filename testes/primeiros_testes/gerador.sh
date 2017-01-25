#!/bin/bash

measurement='octets'

type=$(((RANDOM%3)+1))

srcAS=$(((RANDOM%5)+1))
dstAS=$(((RANDOM%5)+1))
while [ $srcAS -eq $dstAS ]; do
	dstAS=$(((RANDOM%5)+1))
done 

ipversion[1]='IPv4'
ipversion[2]='IPv6'

direction[1]='in'
direction[2]='out'

case $type in
	1)
		prefix=$(((RANDOM%5)+1))
		echo $measurement,'type=ATM','srcAS=AS'$srcAS,'dstAS=AS'$dstAS,'ipversion='${ipversion[$(((RANDOM%2)+1))]},prefix='150.164.8.0_2'$prefix,'direction='${direction[$(((RANDOM%2)+1))]} 'value='$(((RANDOM<<15)|RANDOM)) $(($(date +%s%N)/1000000))
		;;
  	2)
		vlan=$(((RANDOM%5)+1))
     	echo $measurement,'type=ATB','vlan='$vlan,'srcAS=AS'$srcAS,'dstAS=AS'$dstAS,'ipversion='${ipversion[$(((RANDOM%2)+1))]},'direction='${direction[$(((RANDOM%2)+1))]} 'value='$(((RANDOM<<15)|RANDOM)) $(($(date +%s%N)/1000000))
		;;
  	3)
		subtype[1]='BGP'
		subtype[2]='ICMP'
     	echo $measurement,'type=BGP','srcAS=AS'$srcAS,'dstAS=AS'$dstAS,'ipversion='${ipversion[$(((RANDOM%2)+1))]},'subtype='${subtype[$(((RANDOM%2)+1))]]},'direction='${direction[$(((RANDOM%2)+1))]} 'value='$(((RANDOM<<15)|RANDOM)) $(($(date +%s%N)/1000000))
		;;
	*)
		echo 'error'	
		;;
esac
