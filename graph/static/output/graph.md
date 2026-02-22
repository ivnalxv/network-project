graph LR
%% Терминал
	3[Терминал node_n1]:::terminal
	4[Терминал node_n2]:::terminal
	5[Терминал node_n3]:::terminal
	6[Терминал node_n4]:::terminal

%% Коммутаторы
	1[Коммутатор switch_sw1]:::switch
	2[Коммутатор switch_sw2]:::switch

%% Узлы-ребра
	7["edge_from_[switch_sw1_1_+K]_to_[switch_sw2_2_-K]"]:::edgenode
	8["edge_from_[switch_sw1_2_-K]_to_[switch_sw2_1_+K]"]:::edgenode
	9["edge_from_[switch_sw1_9_+K]_to_[switch_sw2_10_-K]"]:::edgenode
	10["edge_from_[switch_sw1_10_-K]_to_[switch_sw2_9_+K]"]:::edgenode
	11["edge_from_[switch_sw1_17_+K]_to_[switch_sw2_18_-K]"]:::edgenode
	12["edge_from_[switch_sw1_18_-K]_to_[switch_sw2_17_+K]"]:::edgenode
	13["edge_from_[switch_sw1_25_+K]_to_[switch_sw2_26_-K]"]:::edgenode
	14["edge_from_[switch_sw1_26_-K]_to_[switch_sw2_25_+K]"]:::edgenode
	15["edge_from_[switch_sw1_3_+Z]_to_[node_n1_1_+K]"]:::edgenode
	16["edge_from_[switch_sw1_11_+Z]_to_[node_n2_1_+K]"]:::edgenode
	17["edge_from_[switch_sw2_1_+K]_to_[switch_sw1_2_-K]"]:::edgenode
	18["edge_from_[switch_sw2_2_-K]_to_[switch_sw1_1_+K]"]:::edgenode
	19["edge_from_[switch_sw2_9_+K]_to_[switch_sw1_10_-K]"]:::edgenode
	20["edge_from_[switch_sw2_10_-K]_to_[switch_sw1_9_+K]"]:::edgenode
	21["edge_from_[switch_sw2_17_+K]_to_[switch_sw1_18_-K]"]:::edgenode
	22["edge_from_[switch_sw2_18_-K]_to_[switch_sw1_17_+K]"]:::edgenode
	23["edge_from_[switch_sw2_25_+K]_to_[switch_sw1_26_-K]"]:::edgenode
	24["edge_from_[switch_sw2_26_-K]_to_[switch_sw1_25_+K]"]:::edgenode
	25["edge_from_[switch_sw2_3_+Z]_to_[node_n3_1_+K]"]:::edgenode
	26["edge_from_[switch_sw2_11_+Z]_to_[node_n4_1_+K]"]:::edgenode
	27["edge_from_[node_n1_1_+K]_to_[switch_sw1_3_+Z]"]:::edgenode
	28["edge_from_[node_n2_1_+K]_to_[switch_sw1_11_+Z]"]:::edgenode
	29["edge_from_[node_n3_1_+K]_to_[switch_sw2_3_+Z]"]:::edgenode
	30["edge_from_[node_n4_1_+K]_to_[switch_sw2_11_+Z]"]:::edgenode

%% Ребры графа
	1 ---> 7
	1 ---> 8
	1 ---> 9
	1 ---> 10
	1 ---> 11
	1 ---> 12
	1 ---> 13
	1 ---> 14
	1 ---> 15
	1 ---> 16
	7 ---> 2
	8 ---> 2
	9 ---> 2
	10 ---> 2
	11 ---> 2
	12 ---> 2
	13 ---> 2
	14 ---> 2
	15 ---> 3
	16 ---> 4
	2 ---> 17
	2 ---> 18
	2 ---> 19
	2 ---> 20
	2 ---> 21
	2 ---> 22
	2 ---> 23
	2 ---> 24
	2 ---> 25
	2 ---> 26
	17 ---> 1
	18 ---> 1
	19 ---> 1
	20 ---> 1
	21 ---> 1
	22 ---> 1
	23 ---> 1
	24 ---> 1
	25 ---> 5
	26 ---> 6
	3 ---> 27
	27 ---> 1
	4 ---> 28
	28 ---> 1
	5 ---> 29
	29 ---> 2
	6 ---> 30
	30 ---> 2

        
classDef terminal fill:#F45B69,stroke:#333,stroke-width:2px
        classDef switch fill:#688EB6,stroke:#333,stroke-width:2px
        classDef edgenode fill:#E4FDE1,stroke:#333,stroke-width:2px
