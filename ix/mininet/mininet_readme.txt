cd blablabla/guilherme

#> sudo ./sdx-mininet.py

Limpar controlador, habilitar STP para loop na rede e configurar switch para encaminahr pacotes sem Openflow

Repetir os comandos abaixo para o bgpmg tbm (tirar o for e rodar na mao o comando interno para bgpmg no lugar de sw$i)
Teste com o ping dentro do mininet para ver se ainda esta perdendo pacotes. Teste bom e: AS1r1 ping 10.1.1.253 (rs1)

# Deletar controlador dos switches criados
for i in $(seq 6) ; do sudo ovs-vsctl del-controller sw$i; done

# Habilitar STP para evitar loop na topologia sem o controlador 
for i in $(seq 6) ; do sudo ovs-vsctl --no-wait set bridge sw$i stp_enable=true; done

# Configurar os switches OF para encaminhar trafego normalmente (atuar como sw normal)  
for i in $(seq 6); do sudo ovs-ofctl add-flow sw$i actions=NORMAL; done

Esperar rotas convergirem

mininet> rs1 ip route (ver se subiu todas as rotas, demora 1 minuto)

Se nao subir, logar no rs1 (xterm rs1) e verificar o quagga
rs1> telnet localhost 2605
senha: sdnip
#> show ip bgp summary (ver se as conexoes bgp subiram)
#> outra coisa legal é ver os vizinhos 
#> show ip bgp neighbors 10.1.1.1 advertised-routes


# Corrigir mininet quando trava
#> sudo mn -c



Comando mininet uteis:

xterm HOST (abrir terminal no host, switch, ...)

HOST command HOST (executar um comando de um host para outro, ex ping)

tem outros comandos que vc pode usar no mininet. So usar um help para visualizar. Ex: mininet> pingall

Para um iperf, vc pode abrir o xterm no host ou usar o comando iperf host1 host2

