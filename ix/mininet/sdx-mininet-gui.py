#!/usr/bin/env python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info, debug
from mininet.node import Host, RemoteController, OVSKernelSwitch
import os
import sys

QUAGGA_DIR = '/usr/lib/quagga'
QUAGGA_RUN_DIR = '/var/run/quagga'
CONFIG_DIR = 'sdx-configs'

class SdnIpHost(Host):
    def __init__(self, name, ip, route, *args, **kwargs):
        Host.__init__(self, name, ip=ip, *args, **kwargs)

        self.route = route

    def config(self, **kwargs):
        Host.config(self, **kwargs)

        debug("configuring route %s" % self.route)

        self.cmd('ip route add default via %s' % self.route)

class Router(Host):
    def __init__(self, name, quaggaConfFile, zebraConfFile, intfDict, *args, **kwargs):
        Host.__init__(self, name, *args, **kwargs)

        self.quaggaConfFile = quaggaConfFile
        self.zebraConfFile = zebraConfFile
        self.intfDict = intfDict

    def config(self, **kwargs):
        Host.config(self, **kwargs)
        self.cmd('sysctl net.ipv4.ip_forward=1')

        for intf, attrs in self.intfDict.items():
            self.cmd('ip addr flush dev %s' % intf)
            if 'mac' in attrs:
                self.cmd('ip link set %s down' % intf)
                self.cmd('ip link set %s address %s' % (intf, attrs['mac']))
                self.cmd('ip link set %s up ' % intf)
            for addr in attrs['ipAddrs']:
                self.cmd('ip addr add %s dev %s' % (addr, intf))
            if 'rotaONOS' in attrs:
                self.cmd('ip route add 172.17.0.0/16 via 10.10.10.2')
            if 'vlan' in attrs:
                self.cmd( 'ifconfig %s inet 0' % intf )
	        self.cmd('vconfig add %s %d' % (intf, attrs['vlan']))
                self.cmd('ifconfig %s.%d inet %s' % ( intf, attrs['vlan'], addr ))
	    if 'vlan2IP' in attrs:
	        self.cmd('vconfig add %s %d' % (intf, attrs['vlan2']))
                self.cmd('ifconfig %s.%d inet %s' % ( intf, attrs['vlan2'], attrs['vlan2IP']))

        self.cmd('/usr/lib/quagga/zebra -d -f %s -z %s/zebra%s.api -i %s/zebra%s.pid' % (self.zebraConfFile, 
            QUAGGA_RUN_DIR, self.name, QUAGGA_RUN_DIR, self.name))
        self.cmd('/usr/lib/quagga/bgpd -d -f %s -z %s/zebra%s.api -i %s/bgpd%s.pid' % (self.quaggaConfFile, 
            QUAGGA_RUN_DIR, self.name, QUAGGA_RUN_DIR, self.name))

    def terminate(self):
        self.cmd("ps ax | egrep 'bgpd%s.pid|zebra%s.pid' | awk '{print $1}' | xargs kill" % (self.name, self.name))

        Host.terminate(self)

class SdnIpTopo( Topo ):
    
    def build( self ):
        
        # Add western region switches
        west1 = self.addSwitch('sw1', dpid='00000000000000a1', protocols='OpenFlow10')
        west2 = self.addSwitch('sw2', dpid='00000000000000a2', protocols='OpenFlow10')
        # Add core switches
        core1 = self.addSwitch('sw3', dpid='00000000000000a3', protocols='OpenFlow10')
        core2 = self.addSwitch('sw4', dpid='00000000000000a4', protocols='OpenFlow10')
        
        # Add eastern region switches
        east1 = self.addSwitch('sw5', dpid='00000000000000a5', protocols='OpenFlow10')
        east2 = self.addSwitch('sw6', dpid='00000000000000a6', protocols='OpenFlow10')
	
        # Add additional switch so that BGP routers can have presence on local network
        bgpmg = self.addSwitch('bgpmg', dpid='00000000000000a9')

        zebraConf = '%s/zebra.conf' % CONFIG_DIR

        # West switches we want to attach our routers to, in the correct order
        attachmentSwitches = [west1, west2, east1, east2, core2]
        routersVLANs = [10, 10, 50, 10, 10]

        for i in range(1, 5+1):
            name = 'AS%sr1' % i

	    if i  in {1, 2}:
           	 eth0 = { 'mac' : '00:00:00:01:0%s:01' % i,
	                  'ipAddrs' : ['10.1.1.%s/24' % i], 'vlan': routersVLANs[i-1], 'vlan2IP': '172.16.0.%s/24' % i, 'vlan2': 250 }
            else:
           	 eth0 = { 'mac' : '00:00:00:01:0%s:01' % i,
	                  'ipAddrs' : ['10.1.1.%s/24' % i], 'vlan': routersVLANs[i-1] }


            eth1 = { 'ipAddrs' : ['192.168.%s.254/24' % i] }
            intfs = { '%s-eth0' % name : eth0,
                      '%s-eth1' % name : eth1 }

            quaggaConf = '%s/quagga%s.conf' % (CONFIG_DIR, i)

            router = self.addHost(name, cls=Router, quaggaConfFile=quaggaConf,
                                  zebraConfFile=zebraConf, intfDict=intfs)
            
            host = self.addHost('AS%sh1' % i, cls=SdnIpHost, 
                                ip='192.168.%s.1/24' % i,
                                route='192.168.%s.254' % i)
            
            self.addLink(router, attachmentSwitches[i-1])
            self.addLink(router, host)

        # Wire up the switches in the topology
        self.addLink( west1, west2)
        self.addLink( west1, core1)
        self.addLink( west2, core2)
        self.addLink( core1, core2)
        self.addLink( core1, east1)
        self.addLink( core2, east2)
        self.addLink( east1, east2)

        # Set up the internal West BGP speaker
        rs1Eth0 = { 'mac':'00:00:00:00:00:01', 
                        'ipAddrs' : ['10.1.1.253/24',], 'vlan': 10 }
	rs1Eth1 = { 'ipAddrs' : ['10.10.10.31/24'], 'rotaONOS': '10.10.10.2' }
        rs1Intfs = { 'rs1-eth0' : rs1Eth0,
                         'rs1-eth1' : rs1Eth1 }
        
        rs1 = self.addHost( 'rs1', cls=Router, 
                             quaggaConfFile = '%s/rs1-quagga-sdn.conf' % CONFIG_DIR, 
                             zebraConfFile = zebraConf, 
                             intfDict=rs1Intfs, inNamespace=True )
        
        self.addLink( rs1, west1 )
        self.addLink( rs1, bgpmg )

        # Set up the internal East BGP speaker
        rs2Eth0 = { 'mac':'00:00:00:00:00:02',
                        'ipAddrs' : ['10.1.1.254/24',], 'vlan': 10 }
        rs2Eth1 = { 'ipAddrs' : ['10.10.10.32/24'], 'rotaONOS':'10.10.10.2' }
        rs2Intfs = { 'rs2-eth0' : rs2Eth0,
                         'rs2-eth1' : rs2Eth1 }
        
        rs2 = self.addHost( 'rs2', cls=Router,
                             quaggaConfFile = '%s/rs2-quagga-sdn.conf' % CONFIG_DIR,
                             zebraConfFile = zebraConf, 
                             intfDict=rs2Intfs, inNamespace=True )
        
        self.addLink( rs2, east1 )
	self.addLink( rs2, bgpmg )

        # Set up the internal East BGP speaker
        #quar1Eth0 = { 'mac':'00:00:00:00:00:03',
        quar1Eth0 = { 'mac':'00:00:00:00:00:03',
                        'ipAddrs' : ['10.1.1.253/24',], 'vlan': 10 }
        quar1Eth1 = { 'ipAddrs' : ['10.10.10.33/24'], 'rotaONOS':'10.10.10.2' }
        quar1Intfs = { 'quar1-eth0' : quar1Eth0,
                         'quar1-eth1' : quar1Eth1 }
        
        quar1 = self.addHost( 'quar1', cls=Router,
                             quaggaConfFile = '%s/rs1-quarentena-sdn.conf' % CONFIG_DIR,
                             zebraConfFile = zebraConf, 
                             intfDict=quar1Intfs, inNamespace=True )
        
        self.addLink( quar1, east2 )
	self.addLink( quar1, bgpmg )




def run():
    topo = SdnIpTopo()
    controllers = sys.argv
    net = Mininet( topo=topo, controller=None )
    net.addController( 'onos1', controller=RemoteController, ip=controllers[1], port=6633 )
 #   net.addController( 'onos2', controller=RemoteController, ip=controllers[2], port=6633 )
 #   net.addController( 'onos3', controller=RemoteController, ip=controllers[3], port=6633 )
    net.start()
    os.system('ovs-vsctl del-controller bgpmg') # BGP Mgmt switch does not need controllers
    #os.system('ovs-vsctl add-port bgpmg eth1') # Add external port to BGP Mgmt switch
    os.system('ovs-ofctl add-flow bgpmg actions=NORMAL') # BGP Mgmt switch should forward normal
 #   os.system('ip addr flush dev eth1') # Remove original IP from external port eth1
    os.system('ip addr add 10.10.10.2/24 dev bgpmg') # Add original eth1 IP to BGP Mgmt switch
    os.system('ip addr add 10.10.10.1/24 dev bgpmg-eth1') # Add original eth1 IP to BGP Mgmt switch
    os.system('ip addr add 10.10.10.3/24 dev bgpmg-eth2') # Add original eth1 IP to BGP Mgmt switch
    CLI(net)
    net.stop()
 #   os.system('ip addr add 10.10.10.2/24 dev eth1') # Add original eth1 IP back when done
    info("done\n")

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
