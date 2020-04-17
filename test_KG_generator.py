##########Created by: Sanjukta Krishnagopal#########
##################April 2020#######################

import pandas as pd
import spacy
nlp = spacy.load('en_core_web_sm')
from spacy.matcher import Matcher 
from spacy.tokens import Span 
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm


 ### account for compound words, i.e., identify blue sky as subject instead of just sky###
 
def get_entities(sent):
      ent1 = ""
      ent2 = ""

      prv_tok_dep = ""    
      prv_tok_text = ""  

      prefix = ""
      modifier = ""

      for tok in nlp(sent):
        if tok.dep_ != "punct":
          if tok.dep_ == "compound":
            prefix = tok.text
            # if the previous word was also a 'compound' then add the current word to it
            if prv_tok_dep == "compound":
              prefix = prv_tok_text + " "+ tok.text

          if tok.dep_.endswith("mod") == True:
            modifier = tok.text
            # if the previous word was also a 'compound' then add the current word to it
            if prv_tok_dep == "compound":
              modifier = prv_tok_text + " "+ tok.text

          if tok.dep_.find("subj") == True:
            ent1 = modifier +" "+ prefix + " "+ tok.text
            prefix = ""
            modifier = ""
            prv_tok_dep = ""
            prv_tok_text = ""      

          if tok.dep_.find("obj") == True:
            ent2 = modifier +" "+ prefix +" "+ tok.text

          # update variables
          prv_tok_dep = tok.dep_
          prv_tok_text = tok.text

          return [ent1.strip(), ent2.strip()]

  
###get the relationship between subject and object###

def get_relation(sent):

      doc = nlp(sent)
      # Matcher class object 
      matcher = Matcher(nlp.vocab)

      #define the pattern 
      pattern = [{'DEP':'ROOT'}, 
                {'DEP':'prep','OP':"?"},
                {'DEP':'agent','OP':"?"},  
                {'POS':'ADJ','OP':"?"}]
      
      # follow-up words of form prep/agent as adj gets added to the matcher
      matcher.add("matching_1", None, pattern) 

      #identifies the verb
      matches = matcher(doc)
      k = len(matches) - 1
      span = doc[matches[k][1]:matches[k][2]] 
      return(span.text)

  

# import sample file
test_sentences = pd.read_csv("test.csv")

#extract subject-object pairs for all sentences
entity_pairs = []
for i in tqdm(test_sentences["sentence"]):
  entity_pairs.append(get_entities(i))

source = [i[0] for i in entity_pairs]
target = [i[1] for i in entity_pairs]

#extract all relationships
relations = [get_relation(i) for i in tqdm(test_sentences['sentence'])]

#create pandas dataframe
kg_df = pd.DataFrame({'source':source, 'target':target, 'edge':relations})

# create a directed-graph using NetworkX
#showing all relationships is very cluttered - hence show all relationships with edge corresponsing to a specific relation
G=nx.from_pandas_edgelist(kg_df[kg_df['edge']=="written by"], "source", "target", edge_attr=True, create_using=nx.MultiDiGraph())

#plot
plt.figure()
pos = nx.spring_layout(G, k = 0.3) # k regulates the distance between nodes
nx.draw(G, with_labels=True, node_color='red', node_size=1000, edge_cmap=plt.cm.Blues, pos = pos)
plt.show()
