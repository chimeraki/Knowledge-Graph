########     Code By: Sanjukta Krishnagopal - April 2020     #########
############ Analysis of Edge attributes on a Knowledge Graph ########

import networkx as nx
from collections import Counter
import spacy
import pandas as pd
import numpy as np

node_list = []
EDGES = []
d = {}

edges_links = pd.read_csv('entities_links_extracted.csv')

edges_links = pd.read_csv('entities_links_extracted.csv')
source = edges_links.start_node
target = edges_links.end_node
relations = edges_links.relation

#creating Digraph with edge relations
kg_df = pd.DataFrame({'source':source, 'target':target, 'relation':relations})

G=nx.from_pandas_edgelist(kg_df,"source", "target", edge_attr=True, create_using=nx.DiGraph())

#calculating edge weights
EDGES=[]
for i in range(len(source)):

    node1 = source[i]
    node2 = target[i]
    EDGES.append( (node1, node2) )
cnt=Counter(EDGES)

# adding attributes to the graph
d={}
for k in cnt.keys():
    d[k]={}
    d[k]['weight']=cnt[k]
    #add additional attributes here for an edge between two nodes. The attributes can be a list with all the dates for instance

nx.set_edge_attributes(G, d)


#extracting edges with highest weights
s=[]
for (u,v) in G.edges():
    w=G[u][v]['weight']
    if w>1:
        s.append([(u,v),w])
s=np.array(s)

edge_imp=s[s[:,1].astype('float64').argsort()[::-1]] #most important edges
with open('edge_importance.csv', 'w') as f:
      writer = csv.writer(f)
      writer.writerows(edge_imp)

#extracting unique relations of high weight edges
l=[]
for (u,v) in edge_imp[:,0]:
    r=G[u][v]['relation']
    l.extend(r)
c=Counter(l)
#extracting unique relations that have occured less than 3 times
inter=[k for k, v in c.items() if v <3]

imp_rel=[]
for (u,v) in edge_imp[:,0]:
    r=G[u][v]['relation']
    w=G[u][v]['weight']
    for n in r:
        if n in inter:
            imp_rel.append([(u,v),n,w])
    
imp_rel=np.array(imp_rel)

#saving to csv file
with open('unique_relationships.csv', 'w') as f:
      writer = csv.writer(f)
      writer.writerows(imp_rel)
