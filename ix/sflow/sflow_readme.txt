sflow - informações uteis


sflowtool (ferramenta para coletar)
http://sflow.org/discussion/sflow-discussion/0116.html
http://openvswitch.org/support/config-cookbooks/sflow/


# MININET (habilitar sflow nos switches). Ex para o sw5, mas tem que ser feito para todos

sudo ovs-vsctl -- --id=@sflow create sflow agent=eth0  target=\"127.0.0.1:6343\" sampling=20 polling=20 -- set bridge sw5 sflow=@sflow

# Programa de coletor do próprio pessoal do sflow
/home/mininet/sflow-rt
mininet@mininet-vm:~/sflow-rt$ ./start.sh 


# Visualizar as bridges (switches) no sistema
mininet@mininet-vm:~$ sudo ovs-vsctl list br

# Influxdb
Sumarizar pelo mac
curl -H "Content-Type:application/json" -X PUT --data "{value:'bytes',filter:'ipsource=10.0.0.1'}" http://localhost:8008/flow/h1/json

http://localhost:8008/metric/ALL/h2,h1/html

Sumarizar pelo AS1
curl -H "Content-Type:application/json" -X PUT --data "{value:'bytes',filter:'macsource=000000010201'}" http://localhost:8008/flow/AS2_OUT/json 

curl -H "Content-Type:application/json" -X PUT --data "{value:'bytes',filter:'macdestination=000000010201'}" http://localhost:8008/flow/AS2_IN/json 

via REST-API 
http://localhost:8008/metric/ALL/dashboard_example_bytes,sum:ifinoctets,sum:ifoutoctets/html


Jeito elegante: sflow
http://blog.sflow.com/2010/05/configuring-open-vswitch.html

DDoS SDN
http://pt.slideshare.net/chaochen5245961/cc3736-slides

Graphite SFLOW
http://blog.sflow.com/2013/11/metric-export-to-graphite.html