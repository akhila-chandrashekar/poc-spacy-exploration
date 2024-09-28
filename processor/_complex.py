# import re
import spacy


class ComplexFunc:
    # """docstring for Tenses."""

    def __init__(self):
        self.ent_pairs = list()
        self.nlp = spacy.load('en_core_web_lg')

    def get_time_place_from_sent(self,sentence):
        xdate =[]
        xplace =[]
        for i in sentence.ents:
            if i.label_ in ('DATE'):
                xdate.append(str(i))

            if i.label_ in ('GPE'):
                xplace.append(str(i))

        return xdate, xplace

    def find_obj(self, sentence, place, time, return_labels=False):
        object_list = []  # List to store object and label tuples (object, label)
        buffer_obj = None
        object_labels = []
        for word in sentence:
            # Check if the word is an object (direct object, prepositional object, etc.)
            if word.dep_ in ('obj', 'dobj', 'pobj'):
                buffer_obj = word

                # Skip if the object is a place preceded by 'of'
                if str(word) in place and word.nbor(-1).dep_ == 'prep' and str(word.nbor(-1)) == "of":
                    pass
                else:
                    # Check if the word is not in time or place entities
                    if str(word) not in time and str(word) not in place:
                        # Traverse through the subtree of the word to capture related objects
                        for child in word.subtree:
                            if child.dep_ in ('conj', 'dobj', 'pobj', 'obj') and str(child) not in time and str(child) not in place:
                                if [i for i in child.lefts]:
                                    if child.nbor(-1).dep_ == 'nummod' and child.dep_ in ('dobj', 'obj', 'pobj'):
                                        ichild = str(child.nbor(-1)) + " " + str(child)
                                        object_list.append(str(ichild))
                                        object_labels.append(child.dep_)

                                    elif child.nbor(-1).dep_ == 'punct':
                                        if child.nbor(-2).dep_ == 'compound':
                                            # Handling compound objects like "ice-cream"
                                            ichild = str(child.nbor(-2)) + str(child.nbor(-1)) + str(child)
                                            object_list.append(str(ichild))
                                            object_labels.append(child.dep_)
                                        elif child.nbor(-2).dep_ == 'amod':
                                            # Handling adjectives, e.g., "social-distancing"
                                            ichild = str(child.nbor(-2)) + str(child.nbor(-1)) + str(child)
                                            object_list.append(str(ichild))
                                            object_labels.append(child.dep_)

                                    elif child.nbor(-1).dep_ == 'compound':
                                        # Handling compound objects
                                        child_with_comp = ""
                                        for i in child.subtree:
                                            if i.dep_ in ('compound', 'nummod', 'quantmod'):
                                                if child_with_comp == "":
                                                    child_with_comp = str(i)
                                                else:
                                                    child_with_comp = child_with_comp + " " + str(i)
                                            elif i.dep_ == 'cc':  # conjunction break
                                                break
                                        ichild = child_with_comp + " " + str(child)
                                        object_list.append(str(ichild))
                                        object_labels.append(child.dep_)

                                    elif child.nbor(-1).dep_ == 'det':
                                        # Handling definite articles, e.g., "The Taj Mahal"
                                        object_list.append(str(child))
                                        object_labels.append(child.dep_)

                                elif [i for i in child.rights]:
                                    # Capturing right-side dependencies of the object
                                    if str(child.text) not in [obj[0] for obj in object_list]:
                                        object_list.append(str(child.text))
                                        object_labels.append(child.dep_)

                                    # Handling conjunctions
                                    for a in child.children:
                                        if a.dep_ == 'conj':
                                            if a.nbor(-1).dep_ != 'punct':
                                                object_list.append(str(a.text))
                                                object_labels.append(a.dep_)

                                else:
                                    # Capture the single object if no children exist
                                    if str(child) not in [obj[0] for obj in object_list]:
                                        object_list.append(str(child))
                                        object_labels.append(child.dep_)

                    elif str(word) in place and str(word.nbor(-1)) != "of":
                        if not object_list:
                            object_list.append(str(word))
                            object_labels.append(word.dep_)
                    else:
                        if str(word) in time and not object_list:
                            object_list.append(str(word))
                            object_labels.append(word.dep_)

        return object_list, object_labels, buffer_obj


    def find_subj(self, sentence, return_labels=False):
        subject_list = []
        subject_labels = []

        # SUBJECT FINDING loop
        dep_word = [word.dep_ for word in sentence]
        word_dep_count_subj = [dep_word.index(word) for word in dep_word if word in ('nsubj', 'subj', 'nsubjpass')]
        
        if word_dep_count_subj:
            word_dep_count_subj = word_dep_count_subj[0] + 1
        else:
            word_dep_count_subj = 1

        subject_final = ""
        # subject_label = None
        print('*******', word_dep_count_subj)
        for word in sentence:
            print(word.dep_)
            if word_dep_count_subj > 0:
                if word.dep_ in ('compound', 'nmod', 'amod', 'poss', 'case', 'nummod'):
                    if subject_final == "":
                        subject_final = str(word)
                        print('1',subject_final, word.ent_type_)
                        word_dep_count_subj -= 1
                    elif word.dep_ == 'case':
                        subject_final = subject_final + "" + str(word)
                        print('2', subject_final)
                        word_dep_count_subj -= 1
                    else:
                        subject_final = subject_final + " " + str(word)
                        print('3', subject_final)
                        word_dep_count_subj -= 1
                elif word.dep_ in ('nsubj', 'subj', 'nsubjpass'):
                    if subject_final == "":
                        subject_final = str(word)
                        # subject_label = word.ent_type_  # Capture entity label for the subject
                        # subject_list.extend([str(a.text) for a in word.subtree if a.dep_ in ('conj')])
                        word_dep_count_subj -= 1
                        break
                    else:
                        subject_final = subject_final + " " + str(word)
                        # subject_label = word.ent_type_  # Capture entity label for the subject
                        # subject_list.extend([str(a.text) for a in word.subtree if a.dep_ in ('conj')])
                        word_dep_count_subj -= 1
                        break
                else:
                    pass

        subject_list.append(subject_final)
        
        # if return_labels:
        #     subject_labels.append(subject_label if subject_label else "UNKNOWN")  # Add subject label if available
        if return_labels:
        # Check if the subject matches any named entities
            entity_label = 'UNKNOWN'
            for token in sentence:
                if str(token) in subject_final:
                    entity_label = token.ent_type_ if token.ent_type_ else 'UNKNOWN'
                    break  # Break once we find the entity type
        
            subject_labels.append(entity_label)

        print('^^^^', subject_labels)    

        if return_labels:
            return subject_list, subject_labels
        else:
            return subject_list


    def find_relation(self, buffer_obj):
        aux_relation = ""
        
        # Check if buffer_obj is None
        if buffer_obj is None:
            return 'unknown', aux_relation

        print(f"buffer_obj type: {type(buffer_obj)}; token: {buffer_obj.text}")

        # Get the ancestors of the buffer_obj token
        ancestors = list(buffer_obj.ancestors)
        print(f"Ancestors: {[str(a) for a in ancestors]}")  # Debugging output

        # Check for ROOT ancestor
        relation = next((w for w in ancestors if w.dep_ == 'ROOT'), None)

        if relation:
            print('Found relation:', relation.text)
            sp_relation = relation

            # Check if there are valid ancestors
            if len(ancestors) > 0:
                relation = self.extract_relation_from_ancestors(sp_relation)
                aux_relation = self.extract_aux_relation(sp_relation)

        else:
            # Fallback to parent if no ROOT is found
            parent = buffer_obj.head
            if parent:
                print(f"No ROOT found. Parent: {parent.text}")
                relation = parent  # Use the parent as a fallback
            else:
                return 'unknown', aux_relation

        # Determine the relation type
        relation_type = self.determine_relation_type(str(relation))
        print('Relation:', relation, 'Aux:', aux_relation, 'Type:', relation_type)

        return str(relation), aux_relation

    def extract_relation_from_ancestors(self, sp_relation):
        """Extract the relation string from the ancestors."""
        relation = str(sp_relation)
        nbor = sp_relation.nbor(1)

        if nbor.pos_ == 'VERB':
            if len(list(sp_relation.ancestors)) > 2 and sp_relation.nbor(2).dep_ == 'xcomp':
                relation = ' '.join((relation, str(nbor), str(sp_relation.nbor(2))))
            elif len(list(p_relation.ancestors)) > 1 and sp_relation.nbor(1).dep_ == 'xcomp':
                relation += ' ' + str(sp_relation.nbor(1))
        
        elif nbor.dep_ in ('ADP', 'PART') and nbor.dep_ == 'aux' and str(nbor) == 'to':
            relation += " " + str(nbor)
        
        elif len(list(sp_relation.ancestors)) > 1 and nbor.dep_ == 'prep' and str(nbor) == 'to':
            relation += " " + str(nbor)

        return relation

    def extract_aux_relation(self, sp_relation):
        """Extract auxiliary relation from the sp_relation."""
        aux_relation = ""
        if len(list(sp_relation.ancestors)) > 2:
            aux_relation = str(sp_relation.nbor(2)) if str(sp_relation.nbor(2)) != 'and' else ""
        return aux_relation

    def determine_relation_type(self, relation):    
        """Determine the type of relation based on the verb."""

        # Example mapping of relation types to specific verbs or verb patterns
        action_verbs = ['do', 'make', 'create', 'found', 'build', 'announce', 'decide']            
        possession_verbs = ['have', 'own', 'possess', 'hold']
        communication_verbs = ['say', 'tell', 'inform', 'announce']
        movement_verbs = ['go', 'move', 'travel', 'arrive']

        # Convert the relation to lowercase for case-insensitive comparison
        relation_lower = relation.lower()

        # Determine the relation type based on the verb patterns
        if any(verb in relation_lower for verb in action_verbs):
            return 'action'
        elif any(verb in relation_lower for verb in possession_verbs):
            return 'possession'
        elif any(verb in relation_lower for verb in communication_verbs):
            return 'communication'
        elif any(verb in relation_lower for verb in movement_verbs):
            return 'movement'
        else:
            # If the relation doesn't match any known categories, return 'unknown'
            return 'unknown'

    def normal_sent(self, sentence):
        # Extract time and place entities from the sentence
        time, place = self.get_time_place_from_sent(sentence)

        # Initialize lists to store subjects, objects, and their labels
        subject_list, object_list = [], []
        subject_labels, object_labels = [], []

        # Auxiliary relation and a variable for compound relations
        aux_relation, child_with_comp = "", ""

        # Extract subjects and their labels from the sentence
        subject_list, subject_labels = self.find_subj(sentence, return_labels=True)
        
        # Extract objects and their labels from the sentence, considering the place and time entities
        object_list, object_labels, buffer_obj = self.find_obj(sentence, place, time, return_labels=True)
        
        # Extract the main relation, auxiliary relation, and relation type between subjects and objects
        relation, aux_relation = self.find_relation(buffer_obj)

        relation_type = self.determine_relation_type(relation)
        # Initialize the entity pairs list
        self.ent_pairs = []

        # Set the first occurrence of time and place, or an empty string if none
        if time:
            time = time[0]
        else:
            time = ""

        if place:
            place = place[0]
        else:
            place = ""

        # Prepare lists to store subjects and objects along with their labels
        pa, pb = [], []
        print('==============')
        print(subject_list, subject_labels)
        for idx, m in enumerate(subject_list):
            print('---------------------------')
            print(idx)
            pa.append([m, subject_labels[idx]])  # Add subject label

        for idx, n in enumerate(object_list):
            pb.append([n, object_labels[idx]])  # Add object label

        # Create entity pairs combining each subject, object, relation type, time, and place
        for m in range(0, len(pa)):
            for n in range(0, len(pb)):
                self.ent_pairs.append([
                    str(pa[m][1]),              # Subject label
                    str(pa[m][0]).lower(),      # Subject in lowercase
                    str(relation_type),         # Relation type
                    str(relation).lower(),      # Main relation in lowercase
                    str(aux_relation).lower(),  # Auxiliary relation in lowercase
                    str(pb[n][1]),              # Object label
                    str(pb[n][0]).lower(),      # Object in lowercase
                    str(time),                  # Time
                    str(place)                  # Place
                ])

        print(self.ent_pairs)
        # Return the list of entity pairs
        return self.ent_pairs

    def question_pairs(self, question__):
        # questionList = question__.split(" ")
        # print(questionList)

        questionNLPed = self.nlp(question__)
        maybe_object = ([i for i in questionNLPed if i.dep_ in ('obj', 'pobj', 'dobj')])
        # print(maybe_object)
        maybe_place, maybe_time = [], []
        aux_relation = ""
        maybe_time, maybe_place = self.get_time_place_from_sent(questionNLPed)
        object_list = []

        for obj in questionNLPed:
            objectNEW = obj
            # print(obj.dep_)

            # FOR WHO
            if obj.dep_ in ('obj', 'dobj', 'pobj', 'xcomp') and str(obj).lower() != "what":
                buffer_obj = obj

                if obj.dep_ in ('xcomp') and obj.nbor(-1).dep_ in ('aux') and obj.nbor(-2).dep_ in ('ROOT'):
                    # print("here")
                    continue

                if str(obj) in maybe_place and obj.nbor(-1).dep_ in ('prep') and str(obj.nbor(-1)) == "of":
                    # """ INDIA should be in place list + "of" "India" is there then it will come here """
                    pass
                else:
                    if str(obj) not in maybe_time and str(obj) not in maybe_place:
                        # INDIA should not be in place list + INDIA should not be in time list
                        # ice-cream and mangoes
                        for child in obj.subtree:
                            # print(child)
                            if child.dep_ in ('conj', 'dobj', 'pobj', 'obj'):
                                if [i for i in child.lefts]:
                                    if child.nbor(-1).dep_ in ('punct') and child.nbor(-2).dep_ in ('compound'):
                                        # """ice-cream"""
                                        child = str(child.nbor(-2)) + str(child.nbor(-1)) + str(child)
                                        object_list.append(str(child))

                                    elif child.nbor(-1).dep_ in ('compound'):
                                        # print(child)
                                        child_with_comp = ""
                                        for i in child.subtree:
                                            if i.dep_ in ('compound', 'nummod','quantmod'):
                                                if child_with_comp == "":
                                                    child_with_comp = str(i)
                                                else:
                                                    child_with_comp = child_with_comp +" "+ str(i)
                                            elif i.dep_ in ('cc'):
                                                break
                                        child = child_with_comp + " " + str(child)

                                        # ice cream
                                        # print(child)
                                        object_list.append(str(child))

                                    elif child.nbor(-1).dep_ in ('det'):
                                        # The Taj Mahal
                                        object_list.append(str(child))

                                elif [i for i in child.rights]:
                                    if str(child.text) not in object_list:
                                        object_list.append(str(child.text))

                                    for a in child.children:
                                        if a.dep_ in ('conj'):
                                            if a.nbor(-1).dep_ in ('punct'):
                                                pass
                                            else:
                                                object_list.extend( [ str(a.text) ] )

                                else:
                                    # icecream
                                    if str(child) not in object_list:
                                        object_list.append(str(child))

                            elif obj.dep_ in ('xcomp'):
                                object_list.append(str(obj))

                    elif str(obj) in maybe_place and str(obj.nbor(-1)) != "of":
                        object_list.append(str(obj))
                    else:
                        if str(obj) in maybe_time and object_list == []:
                            object_list.append(str(obj))


                # print(object_list)
                obj = object_list[-1]
                # # print(obj)
                # # print(obj.nbor(1))
                # try:
                #     if obj.nbor(-1).pos_ in ('PUNCT') and obj.nbor(-2).pos_ in ('NOUN'):
                #         obj = ' '.join((str(obj.nbor(-2)), str(obj)))
                #     elif obj.nbor(-1).pos_ in ('NOUN'):
                #         obj = ' '.join( (str(obj.nbor(-1)), str(obj) ))
                #     # elif obj.nbor(1).pos_ in ('ROOT'):
                #         # pass
                # except IndexError:
                #     pass

                # elif obj.nbor(1).pos_ in :
                    # print(obj.nbor(1).pos_)

                # print(obj)
                relation = [w for w in objectNEW.ancestors if w.dep_ =='ROOT']
                if relation:
                    relation = relation[0]
                    sp_relation = relation
                    # print(sp_relation)
                    # print(relation)
                    if relation.nbor(1).pos_ in ('ADP', 'PART', 'VERB'):
                        if relation.nbor(2).dep_ in ('xcomp'):
                            aux_relation = str(relation.nbor(2))
                            relation = str(relation)+" "+str(relation.nbor(1))
                        else:# print(relation.nbor(2).dep_)
                            relation = str(relation)
                            # print(relation)

                    subject = [a for a in sp_relation.lefts if a.dep_ in ('subj', 'nsubj','nsubjpass')]  # identify subject nodes
                    # print(subject)
                    if subject:
                        subject = subject[0]
                        # print(subject)
                        # subject, subject_type = self.prepro.refine_ent(subject, question__)
                        # print(subject)
                    else:
                        subject = 'unknown'
                else:
                    relation = 'unknown'

                # obj, object_type = self.prepro.refine_ent(obj, question__)
                # print(subject, relation, obj)
                self.ent_pairs = []

                if maybe_time and maybe_place:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str(maybe_time[0]).lower(), str(maybe_place[0]).lower()])
                elif maybe_time:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str(maybe_time[0]).lower(), str("").lower()])
                elif maybe_place:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str("").lower(), str(maybe_place[0]).lower()])
                else:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str("").lower(), str("").lower()])
                # ent_pairs.append([str(subject), str(relation), str(obj)])
                # print(self.ent_pairs)
                return self.ent_pairs

            elif str(obj).lower() == "what":
                relation = [w for w in objectNEW.ancestors if w.dep_ =='ROOT']
                if relation:
                    relation = relation[0]
                    sp_relation = relation
                    if relation.nbor(1).pos_ in ('ADP', 'PART', 'VERB'):
                        if relation.nbor(2).dep_ in ('xcomp'):
                            aux_relation = str(relation.nbor(2))
                            relation = str(relation)+" "+str(relation.nbor(1))
                        else:# print(relation.nbor(2).dep_)
                            relation = str(relation)
                            # print(relation)

                    subject = self.find_subj(questionNLPed)
                    # print(subject)
                    subject = subject[-1]

                    # subject = [a for a in sp_relation.lefts if a.dep_ in ('subj', 'nsubj','nsubjpass')]  # identify subject nodes
                    # print(subject)
                    # if subject:
                        # subject = subject[0]
                        # print(subject)
                        # subject, subject_type = self.prepro.refine_ent(subject, question__)
                        # print(subject)
                    # else:
                        # subject = 'unknown'
                else:
                    relation = 'unknown'

                # obj, object_type = self.prepro.refine_ent(obj, question__)
                # print(obj)
                self.ent_pairs = []
                # print(subject,relation,obj)
                if maybe_time and maybe_place:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str(maybe_time[0]).lower(), str(maybe_place[0]).lower()])
                elif maybe_time:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str(maybe_time[0]).lower(), str("").lower()])
                elif maybe_place:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str("").lower(), str(maybe_place[0]).lower()])
                else:
                    self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(obj).lower(), str("").lower(), str("").lower()])
                # ent_pairs.append([str(subject), str(relation), str(obj)])
                # print(self.ent_pairs)
                return self.ent_pairs

            elif obj.dep_ in ('advmod'):
                # print(str(obj).lower())
                if str(obj).lower() == 'where':
                    relation = [w for w in obj.ancestors if w.dep_ =='ROOT']
                    # print(relation)
                    if relation:
                        relation = relation[0]
                        sp_relation = relation
                        # print(relation)
                        if relation.nbor(1).pos_ in ('ADP', 'PART', 'VERB'):
                            if relation.nbor(2).dep_ in ('xcomp'):
                                aux_relation = str(relation.nbor(2))
                                relation = str(relation)+" "+str(relation.nbor(1))
                            else:# print(relation.nbor(2).dep_)
                                relation = str(relation)
                                # print(relation)

                        # for left_word in sp_relation.lefts:
                        #     if left_word.dep_ in ('subj', 'nsubj','nsubjpass'):
                        #         if [i for i in left_word.lefts]:
                        #             for left_of_left_word in left_word.lefts:
                        #                 subject = str(left_of_left_word) + " " + str(left_word)
                        #         else:
                        #             subject = str(left_word)

                        subject = self.find_subj(questionNLPed)
                        # print(subject)
                        subject = subject[-1]

                        # subject = [a for a in sp_relation.lefts if a.dep_ in ('subj', 'nsubj','nsubjpass')]  # identify subject nodes
                        # # print(subject)
                        # if subject:
                        #     subject = subject[0]
                        #     # print(subject)
                        #     # subject, subject_type = self.prepro.refine_ent(subject, question__)
                        #     # print(subject)
                        # else:
                        #     subject = 'unknown'
                    else:
                        relation = 'unknown'

                    self.ent_pairs = []
                    # print(obj, subject, relation)
                    if maybe_object:
                        if maybe_time and maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str(maybe_time[0]).lower(), str("where").lower()])
                        elif maybe_time:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str(maybe_time[0]).lower(), str("where").lower()])
                        elif maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str("").lower(), str("where").lower()])
                        else:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str("").lower(), str("where").lower()])
                    else:
                        if maybe_time and maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str(maybe_time[0]).lower(), str("where").lower()])
                        elif maybe_time:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str(maybe_time[0]).lower(), str("where").lower()])
                        elif maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str("").lower(), str("where").lower()])
                        else:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str("").lower(), str("where").lower()])

                    # ent_pairs.append([str(subject), str(relation), str(obj)])
                    # print(self.ent_pairs)

                    return self.ent_pairs

                elif str(obj).lower() == 'when':
                    # print(obj)
                    relation = [w for w in obj.ancestors if w.dep_ =='ROOT']
                    # print(relation)
                    if relation:
                        relation = relation[0]
                        sp_relation = relation
                        # print(relation)
                        if relation.nbor(1).pos_ in ('ADP', 'PART', 'VERB'):
                            # print(relation.nbor(1).pos_)
                            if relation.nbor(2).dep_ in ('xcomp'):
                                relation = ' '.join((str(relation), str(relation.nbor(1)), str(relation.nbor(2))))
                            else:# print(relation.nbor(2).dep_)
                                relation = ' '.join((str(relation), str(relation.nbor(1))))
                                # print(relation)

                        for left_word in sp_relation.lefts:
                            if left_word.dep_ in ('subj', 'nsubj','nsubjpass'):
                                if [i for i in left_word.lefts]:
                                    for left_of_left_word in left_word.lefts:
                                        subject = str(left_of_left_word) + " " + str(left_word)
                                else:
                                    subject = str(left_word)
                        # subject = [a for a in sp_relation.lefts if a.dep_ in ('subj', 'nsubj','nsubjpass')]  # identify subject nodes
                        # # print(subject)
                        # if subject:
                        #     subject = subject[0]
                        #     # print(subject)
                        #     # subject, subject_type = self.prepro.refine_ent(subject, question__)
                        #     # print(subject)
                        # else:
                        #     subject = 'unknown'
                    else:
                        relation = 'unknown'

                    self.ent_pairs = []
                    # print(obj, subject, relation)
                    if maybe_object:
                        if maybe_time and maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str("when").lower(), str(maybe_place[0]).lower()])
                        elif maybe_time:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str("when").lower(), str("").lower()])
                        elif maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str("when").lower(), str(maybe_place[0]).lower()])
                        else:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str(maybe_object[-1]).lower(), str("when").lower(), str("").lower()])
                    else:
                        if maybe_time and maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str("when").lower(), str(maybe_place[0]).lower()])
                        elif maybe_time:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str("when").lower(), str("").lower()])
                        elif maybe_place:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str("when").lower(), str(maybe_place[0]).lower()])
                        else:
                            self.ent_pairs.append([str(subject).lower(), str(relation).lower(),str(aux_relation).lower(), str("").lower(), str("when").lower(), str("").lower()])

                    # ent_pairs.append([str(subject), str(relation), str(obj)])
                    # print(self.ent_pairs)
                    return self.ent_pairs
