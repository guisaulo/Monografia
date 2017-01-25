#!/usr/bin/awk -f 
BEGIN { 
} 

#/\<startDatagram\>/ { print } 
/\<unixSecondsUTC\>/ { print }
#/\<samplesInPacket\>/ { print }
#/\<startSample\>/ { print }
/\<sampleType\>/ { print }
/\<in_vlan\>/ { print }
/\<out_vlan\>/ { print }
/\<headerProtocol\>/ { print }
/\<sampledPacketSize\>/ { print }
/\<srcMAC\>/ { print }
/\<dstMAC\>/ { print }
/\<srcIP\>/ { print }
/\<dstIP\>/ { print }
/\<endSample\>/ { print }
#/\<endDatagram\>/ {print }


