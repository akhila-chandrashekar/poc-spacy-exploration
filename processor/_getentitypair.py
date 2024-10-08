# import re

import pandas as pd
import spacy

from processor._complex import ComplexFunc
from processor._resolvedep import change_nouns


class GetEntity:
    """docstring for GetEntity."""

    def __init__(self):
        super(GetEntity, self).__init__()
        self.complex = ComplexFunc()
        self.nlp = spacy.load('en_core_web_sm')
        self.change = change_nouns()

    def preprocess_text(self, input_file):
        text_strip = [text.strip() for text in input_file]
        preprocessed_text = [text for text in text_strip if text not in ('', ' ')]
        text = " ".join(preprocessed_text)
        # """ ADDED CUSTOM SCRIPT """
        text = self.change.resolved(text)
        # """ ___________________ """
        text = self.nlp(text)
        return text

    def get_entity(self, text):
        ent_pairs, final_entity_pairs = [],[]
        sentences = [one_sentence.text.strip() for one_sentence in text.sents]

        for one_sentence in sentences:
            final_entity_pairs = []
            one_sentence = self.nlp(one_sentence)

            dep = [token.dep_ for token in one_sentence]
            print(dep)
            pos = [token.pos_ for token in one_sentence]
            print(pos)
            label = [token.label_ for token in one_sentence.ents]
            print(label)
            normal_sent_ = self.complex.normal_sent(one_sentence)
            print(normal_sent_)
            if normal_sent_:
                for pair in normal_sent_:
                    ent_pairs.append(pair)

                pairs = pd.DataFrame(ent_pairs, columns=['source_label','source', 'relation_type','relation', 'aux_relation', 'target_label','target', 'time', 'place'])
                number_of_ent_pairs = str(len(ent_pairs))

                final_entity_pairs.append(pairs)
        
        print('>>>>>',number_of_ent_pairs)
        if final_entity_pairs:
            return final_entity_pairs, number_of_ent_pairs    
        return None, None

if __name__ == '__main__':
    test = GetEntity()
    text = test.nlp("Akhila works in Airbus. Akhila lives in Bangalore.")
    entities, numbers = test.get_entity(text)
    # print(entities[0])
