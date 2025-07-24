# ccai/nlp/extractor.py

import spacy
from spacy.tokens import Doc

from ccai.core.graph import ConceptGraph
from ccai.core.models import ConceptNode, PropertySpec
from ccai.nlp.primitives import PrimitiveManager

class InformationExtractor:
    """
    Processes natural language to extract a rich set of concepts,
    properties, and relationships, populating the concept graph.
    """
    def __init__(self, graph: ConceptGraph, primitive_manager: PrimitiveManager):
        self.nlp = spacy.load("en_core_web_sm")
        self.graph = graph
        self.primitives = primitive_manager

    def ingest_text(self, text: str):
        """Processes a block of text, running all extraction rules."""
        doc = self.nlp(text)
        print("📝 Starting advanced information extraction...")
        for sent in doc.sents:
            # Run all specialized extraction rules on the sentence
            self._extract_is_a(sent)
            self._extract_has_part(sent)
            self._extract_used_for(sent)
            self._extract_can_do(sent)
            self._extract_agent_action_object(sent)
            self._extract_adjective_property(sent)
            self._extract_alias(sent)
            self._extract_compound_statement(sent)
        print("✅ Text ingestion complete.")

    def _get_or_create_node(self, name: str, ctype: str = "entity") -> ConceptNode:
        """Helper to retrieve a node or create it if it doesn't exist."""
        clean_name = name.lower().strip()
        # Handle pluralization simply for now
        if clean_name.endswith('s') and not clean_name.endswith('ss'):
            singular = clean_name[:-1]
            if self.graph.get_node(singular):
                clean_name = singular
        
        node = self.graph.get_node(clean_name)
        if not node:
            node = ConceptNode(name=clean_name, ctype=ctype)
            self.graph.add_node(node)
        return node

    def _extract_is_a(self, sent: Doc):
        """Extracts 'X is a Y' relationships where Y is a noun."""
        for token in sent:
            if token.dep_ == "ROOT" and token.lemma_ == "be":
                subject = next((c for c in token.children if c.dep_ in ("nsubj", "nsubjpass")), None)
                attribute = next((c for c in token.children if c.dep_ == "attr"), None)
                if subject and attribute and attribute.pos_ in ("NOUN", "PROPN", "ADJ"):
                    print(f"  -> Found IS-A: '{subject.text}' is a '{attribute.text}'")
                    subj_node = self._get_or_create_node(subject.text)
                    attr_node = self._get_or_create_node(attribute.text)
                    self.graph.add_edge(subj_node.name, "is_a", attr_node.name)

    def _extract_has_part(self, sent: Doc):
        """Extracts 'X has Y' (composition) relationships."""
        for token in sent:
            if token.lemma_ == "have":
                subject = next((c for c in token.children if c.dep_ == "nsubj"), None)
                obj = next((c for c in token.children if c.dep_ == "dobj"), None)
                if subject and obj:
                    print(f"  -> Found HAS-PART: '{subject.text}' has '{obj.text}'")
                    subj_node = self._get_or_create_node(subject.text)
                    obj_node = self._get_or_create_node(obj.text)
                    self.graph.add_edge(subj_node.name, "has_part", obj_node.name)

    def _extract_used_for(self, sent: Doc):
        """Extracts 'X is used for Y' (purpose) relationships."""
        for token in sent:
            if token.lemma_ == "use" and token.head.lemma_ == "be":
                subject = next((c for c in token.head.children if c.dep_ == "nsubjpass"), None)
                purpose = next((p.children for p in token.children if p.dep_ == "prep" and p.text == "for"), None)
                if subject and purpose:
                    purpose_token = next(purpose, None)
                    if purpose_token:
                        print(f"  -> Found USED-FOR: '{subject.text}' is used for '{purpose_token.text}'")
                        subj_node = self._get_or_create_node(subject.text)
                        purpose_node = self._get_or_create_node(purpose_token.text, ctype="event")
                        self.graph.add_edge(subj_node.name, "used_for", purpose_node.name)

    def _extract_can_do(self, sent: Doc):
        """Extracts 'X can do Y' (capability) relationships."""
        for token in sent:
            if token.lemma_ == "can" and token.dep_ == "aux":
                subject = next((c for c in token.head.children if c.dep_ == "nsubj"), None)
                action = token.head
                if subject and action:
                    print(f"  -> Found CAN-DO: '{subject.text}' can '{action.lemma_}'")
                    subj_node = self._get_or_create_node(subject.text)
                    action_node = self._get_or_create_node(action.lemma_, ctype="event")
                    self.graph.add_edge(subj_node.name, "can_do", action_node.name)

    def _extract_adjective_property(self, sent: Doc):
        """
        Extracts adjective properties, categorizes them, and applies frequency scoring.
        """
        for token in sent:
            if token.pos_ == "ADJ" and token.dep_ in ("acomp", "amod"):
                subject = token.head if token.dep_ == "amod" else next((c for c in token.head.children if c.dep_ == "nsubj"), None)
                if subject:
                    prop_value = token.text
                    primitive_info = self.primitives.get_info(prop_value)
                    if not primitive_info: continue

                    prop_category, prop_type = primitive_info
                    print(f"  -> Found PROPERTY: '{subject.text}' has '{prop_category}': '{prop_value}' ({prop_type})")
                    node = self._get_or_create_node(subject.text)
                    
                    if prop_category not in node.property_stats:
                        node.property_stats[prop_category] = {}
                    
                    counts = node.property_stats[prop_category]
                    
                    if prop_type == 'slots':
                        # For slots, a new value replaces the old ones for scoring.
                        # This is a simplification; a real system might weigh by recency.
                        counts.clear()

                    counts[prop_value] = counts.get(prop_value, 0) + 1
                    
                    total_count = sum(counts.values())
                    new_specs = []
                    for value, count in counts.items():
                        score = count / total_count if prop_type == 'slots' and total_count > 1 else 1.0
                        new_specs.append(PropertySpec(value=value, score=score))
                        
                    node.properties[prop_category] = new_specs

    def _extract_alias(self, sent: Doc):
        """Extract alias statements like 'X is called Y' or 'X is known as Y'."""
        for token in sent:
            if token.dep_ == "ROOT" and token.lemma_ in {"call", "know"}:
                subject = next((c for c in token.children if c.dep_ in ("nsubj", "nsubjpass")), None)
                obj = None
                if token.lemma_ == "call":
                    obj = next((c for c in token.children if c.dep_ in ("dobj", "attr", "oprd")), None)
                else:  # "known as"
                    prep = next((c for c in token.children if c.dep_ == "prep" and c.text.lower() == "as"), None)
                    if prep:
                        obj = next(prep.children, None)
        """Extracts simple alias statements like 'X is called Y'."""
        for token in sent:
            if token.lemma_ == "call" and token.dep_ == "ROOT":
                subject = next((c for c in token.children if c.dep_ in ("nsubj", "nsubjpass")), None)
                obj = next((c for c in token.children if c.dep_ in ("dobj", "attr", "oprd")), None)
                if subject and obj:
                    print(f"  -> Found ALIAS: '{subject.text}' is called '{obj.text}'")
                    node = self._get_or_create_node(subject.text)
                    alias = obj.text.lower().strip()
                    if alias not in node.aliases:
                        node.aliases.append(alias)
                        
    def _extract_agent_action_object(self, sent: Doc):
        """
        Extracts 'X does Y to Z' (agent-action-object) relationships.
        This captures active voice sentences where an agent performs an action on an object.
        """
        for token in sent:
            # Look for verbs that are the root of the sentence or a main verb
            if token.pos_ == "VERB" and token.dep_ in ("ROOT", "ccomp", "xcomp"):
                # Find the subject (agent)
                agent = next((c for c in token.children if c.dep_ in ("nsubj", "nsubj:pass")), None)
                
                # Find the direct object
                obj = next((c for c in token.children if c.dep_ == "dobj"), None)
                
                # If we have both agent and object, create the relationship
                if agent and obj:
                    action = token.lemma_
                    print(f"  -> Found AGENT-ACTION-OBJECT: '{agent.text}' {action} '{obj.text}'")
                    
                    # Create or get nodes
                    agent_node = self._get_or_create_node(agent.text, ctype="agent")
                    action_node = self._get_or_create_node(action, ctype="event")
                    obj_node = self._get_or_create_node(obj.text)
                    
                    # Add relationships
                    self.graph.add_edge(agent_node.name, "performs", action_node.name)
                    self.graph.add_edge(action_node.name, "affects", obj_node.name)
                    
    def _extract_compound_statement(self, sent: Doc):
        """
        Extracts compound statements like 'a human is an agent that can talk and walk and learn'.
        This handles more complex statements that combine multiple relationships.
        """
        # Check if this is a definition statement with a relative clause
        for token in sent:
            if token.dep_ == "ROOT" and token.lemma_ == "be":
                subject = next((c for c in token.children if c.dep_ in ("nsubj", "nsubjpass")), None)
                attribute = next((c for c in token.children if c.dep_ == "attr"), None)
                
                if subject and attribute:
                    # First, extract the basic is-a relationship
                    print(f"  -> Found IS-A in compound: '{subject.text}' is a '{attribute.text}'")
                    subj_node = self._get_or_create_node(subject.text)
                    attr_node = self._get_or_create_node(attribute.text)
                    self.graph.add_edge(subj_node.name, "is_a", attr_node.name)
                    
                    # Look for a relative clause (that can...)
                    rel_clause = None
                    for child in attribute.children:
                        if child.dep_ == "relcl":
                            rel_clause = child
                            break
                    
                    if rel_clause:
                        # Extract capabilities from the relative clause
                        capabilities = []
                        
                        # First, check if the relative clause has "can"
                        modal = None
                        for child in rel_clause.children:
                            if child.dep_ == "aux" and child.lemma_ == "can":
                                modal = child
                                capabilities.append(rel_clause.lemma_)
                                break
                        
                        # If we found "can", look for coordinated verbs (and walk and learn)
                        if modal:
                            for token in sent:
                                if token.head == rel_clause and token.dep_ == "conj":
                                    capabilities.append(token.lemma_)
                            
                            # Add all capabilities to the subject
                            for capability in capabilities:
                                print(f"  -> Found CAN-DO in compound: '{subject.text}' can '{capability}'")
                                action_node = self._get_or_create_node(capability, ctype="event")
                                self.graph.add_edge(subj_node.name, "can_do", action_node.name)
