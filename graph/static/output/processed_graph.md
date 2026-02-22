graph LR
%% Терминал
	1[Терминал node_n1]:::terminal
	2[Терминал node_n2]:::terminal
	3[Терминал node_n3]:::terminal
	4[Терминал node_n4]:::terminal

%% Коммутаторы
	5[Коммутатор switch_sw1]:::switch
	6[Коммутатор switch_sw2]:::switch

%% Узлы-ребра
	7["edge_-K_1"]:::edgenode
	8["edge_+K_1"]:::edgenode
	9["edge_+K_1"]:::edgenode
	10["edge_-K_1"]:::edgenode
	11["edge_-K_2"]:::edgenode
	12["edge_+K_2"]:::edgenode
	13["edge_+K_2"]:::edgenode
	14["edge_-K_2"]:::edgenode
	15["edge_-K_3"]:::edgenode
	16["edge_+K_3"]:::edgenode
	17["edge_+K_3"]:::edgenode
	18["edge_-K_3"]:::edgenode
	19["edge_-K_4"]:::edgenode
	20["edge_+K_4"]:::edgenode
	21["edge_+K_4"]:::edgenode
	22["edge_-K_4"]:::edgenode
	23["edge_+K_1"]:::edgenode
	24["edge_+Z_1"]:::edgenode
	25["edge_+K_1"]:::edgenode
	26["edge_+Z_2"]:::edgenode
	27["edge_+K_1"]:::edgenode
	28["edge_+Z_1"]:::edgenode
	29["edge_+K_1"]:::edgenode
	30["edge_+Z_2"]:::edgenode

%% Ребры графа
	5 <---> 7
	5 <---> 9
	5 <---> 11
	5 <---> 13
	5 <---> 15
	5 <---> 17
	5 <---> 19
	5 <---> 21
	5 <---> 23
	5 <---> 25
	7 <---> 8
	6 <---> 8
	6 <---> 10
	6 <---> 12
	6 <---> 14
	6 <---> 16
	6 <---> 18
	6 <---> 20
	6 <---> 22
	6 <---> 27
	6 <---> 29
	9 <---> 10
	11 <---> 12
	13 <---> 14
	15 <---> 16
	17 <---> 18
	19 <---> 20
	21 <---> 22
	23 <---> 24
	1 <---> 24
	25 <---> 26
	2 <---> 26
	27 <---> 28
	3 <---> 28
	29 <---> 30
	4 <---> 30

        
classDef terminal fill:#F45B69,stroke:#333,stroke-width:2px
        classDef switch fill:#688EB6,stroke:#333,stroke-width:2px
        classDef edgenode fill:#E4FDE1,stroke:#333,stroke-width:2px
