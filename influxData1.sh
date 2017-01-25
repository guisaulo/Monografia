#!/bin/bash

while read var1 var2; do

	case $var1 in
		"unixSecondsUTC")
			unixSecondsUTC=$var2
			;;	
		"sampleType")
			sampleType=$var2
			;;
		"in_vlan")
			in_vlan=$var2
			;;
		"out_vlan")
			out_vlan=$var2
			;;
		"sampledPacketSize")
			sampledPacketSize=$var2
			;;
		"dstMAC")
			dstMAC=$var2
			;;
		"srcMAC")
			srcMAC=$var2
			;;
		"srcIP")
			srcIP=$var2
			;;
		"dstIP")
			dstIP=$var2
			;;
      "IPProtocol")
         IPProtocol=$var2
         if [ $IPProtocol = "6" ]; then
            IPProtocol="tcp"
         elif [ $IPProtocol = "17" ]; then
            IPProtocol="udp"
         fi
         ;;
	esac

	if [ "$var1" == "endSample" ] && [ "$sampleType" == "FLOWSAMPLE" ]; then
		echo 'octets','ipprotocol='$IPProtocol,'in_vlan='$in_vlan,'out_vlan='$out_vlan,'srcIP='$srcIP,'dstIP='$dstIP,'srcMAC='$srcMAC,'dstMAC='$dstMAC 'value='$sampledPacketSize $unixSecondsUTC  
		in_vlan="NULL"
		out_vlan="NULL"
		sampledPacketSize="NULL"
		dstMAC="NULL"
		srcMAC="NULL"
		srcIP="NULL"
		dstIP="NULL"
		IPProtocol="NULL"		
	fi

done 

