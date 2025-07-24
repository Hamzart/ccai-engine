# ccai/nlp/parser.py

import spacy
import re
from spacy.tokens import Token, Span
from typing import Optional, Dict, Any, List, Tuple

from ccai.core.models import Signal

class QueryParser:
    """
    Uses NLP (spaCy) to parse natural language questions into structured
    Signal objects for the reasoning core.
    """
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def parse_question(self, text: str) -> Optional[Signal]:
        """
        Analyzes the dependency parse of a question to determine user intent.
        """
        cleaned = text.lower().strip()
        cleaned = cleaned.replace("what's", "what is").replace("whats", "what is")
        cleaned = cleaned.replace("who's", "who is").replace("whos", "who is")
        cleaned = cleaned.replace("where's", "where is").replace("wheres", "where is")
        cleaned = cleaned.replace("when's", "when is").replace("whens", "when is")
        cleaned = cleaned.replace("how's", "how is").replace("hows", "how is")
        cleaned = cleaned.replace("why's", "why is").replace("whys", "why is")
        
        doc = self.nlp(cleaned.rstrip('?'))
        
        try:
            sent = next(doc.sents)
        except StopIteration:
            return None

        # --- Enhanced Intent Detection ---
        
        # Check for complex question types first
        comparison_signal = self._parse_comparison_question(sent)
        if comparison_signal:
            return comparison_signal
            
        hypothetical_signal = self._parse_hypothetical_question(sent)
        if hypothetical_signal:
            return hypothetical_signal
            
        temporal_signal = self._parse_temporal_question(sent)
        if temporal_signal:
            return temporal_signal

        # 0. Definition-style questions
        if sent.root.lemma_ in {"define", "describe", "explain", "tell"}:
            obj = self._find_object(sent, sent.root, deps=("dobj", "attr", "pobj"))
            if obj:
                return Signal(origin=obj.text, purpose="QUERY", payload={"ask": "relation.is_a"})

        # 1. Check for Verification Intent (is, does, can)
        # This rule is now more specific: it only triggers if the sentence STARTS with an auxiliary verb.
        if sent[0].pos_ == "AUX" or (len(sent) > 1 and sent[1].pos_ == "AUX"):
            aux_index = 0 if sent[0].pos_ == "AUX" else 1
            subject = self._find_subject(sent)
            root = sent.root

            if subject:
                # "is/are" questions
                if sent[aux_index].lemma_ == 'be':
                    adj_obj = self._find_object(sent, root, deps=("acomp",))
                    if adj_obj:
                        return Signal(origin=subject.text, purpose='VERIFY', payload={'relation': 'has_property', 'target': adj_obj.text})
                    
                    noun_obj = self._find_object(sent, root, deps=("attr", "pobj", "dobj"))
                    if noun_obj:
                        return Signal(origin=subject.text, purpose='VERIFY', payload={'relation': 'is_a', 'target': noun_obj.text})

                # "does/do" questions
                if sent[aux_index].lemma_ == 'do':
                    obj = self._find_object(sent, root, deps=("dobj",))
                    if root.lemma_ == 'have' and obj:
                        return Signal(origin=subject.text, purpose='VERIFY', payload={'relation': 'has_part', 'target': obj.text})
                    else:
                        return Signal(origin=subject.text, purpose='VERIFY', payload={'relation': 'can_do', 'target': root.lemma_})

                # "can" questions
                if sent[aux_index].lemma_ == 'can':
                    return Signal(origin=subject.text, purpose='VERIFY', payload={'relation': 'can_do', 'target': root.lemma_})
        
        # 2. Check for "What" Query Intent
        if "what" in [t.lower_ for t in sent]:
            # Special handling for "what is a X?" or "what is an X?" questions
            is_a_match = re.search(r'what\s+is\s+(?:a|an)\s+([a-z_]+)', sent.text.lower())
            if is_a_match:
                entity = is_a_match.group(1).strip()
                return Signal(origin=entity, purpose="QUERY", payload={"ask": "relation.is_a"})
            
            # Handle "what is X?" questions
            is_match = re.search(r'what\s+is\s+([a-z_]+)', sent.text.lower())
            if is_match:
                entity = is_match.group(1).strip()
                return Signal(origin=entity, purpose="QUERY", payload={"ask": "relation.is_a"})
            
            subject = self._find_subject(sent)
            if not subject: subject = sent.root

            if "is" in [t.text for t in sent] or "are" in [t.text for t in sent]:
                return Signal(origin=subject.text, purpose="QUERY", payload={"ask": "relation.is_a"})
            if "have" in [t.lemma_ for t in sent] or "has" in [t.lemma_ for t in sent] or "properties" in sent.text or "parts" in sent.text:
                return Signal(origin=subject.text, purpose="QUERY", payload={"ask_relation": "has_part"})
            # Handles "what does X do?"
            if ("can" in [t.text for t in sent] or "does" in [t.text for t in sent]) and "do" in [t.lemma_ for t in sent]:
                return Signal(origin=subject.text, purpose="QUERY", payload={"ask_relation": "can_do"})
            if "used for" in sent.text or "purpose" in sent.text or "function" in sent.text:
                return Signal(origin=subject.text, purpose="QUERY", payload={"ask_relation": "used_for"})

        return None

    def _find_subject(self, sent: Span) -> Optional[Token]:
        for token in sent:
            if token.dep_ in ("nsubj", "nsubjpass"):
                return token
        return None
    
    def _find_object(self, sent: Span, root: Token, deps: tuple) -> Optional[Token]:
        for token in root.children:
            if token.dep_ in deps:
                return token
        # Fallback for objects in different phrase structures
        for token in sent:
             if token.dep_ in deps:
                 return token
        return None
        
    def _parse_comparison_question(self, sent: Span) -> Optional[Signal]:
        """Parse comparison questions like 'How does X compare to Y?' or 'What's the difference between X and Y?'"""
        # Check for comparison keywords
        comparison_words = ["compare", "comparison", "difference", "different", "similarities", "similar"]
        has_comparison = any(word in sent.text.lower() for word in comparison_words)
        
        if not has_comparison:
            return None
            
        # Look for two entities being compared
        entities = []
        
        # Check for "between X and Y" pattern
        between_match = re.search(r'between\s+([a-z\s]+)\s+and\s+([a-z\s]+)', sent.text.lower())
        if between_match:
            entities = [between_match.group(1).strip(), between_match.group(2).strip()]
        
        # Check for "X compared to Y" pattern
        compared_to_match = re.search(r'([a-z\s]+)\s+compared\s+to\s+([a-z\s]+)', sent.text.lower())
        if not entities and compared_to_match:
            entities = [compared_to_match.group(1).strip(), compared_to_match.group(2).strip()]
        
        # If we found two entities, create a comparison signal
        if len(entities) == 2:
            return Signal(
                origin=entities[0],
                purpose="QUERY",
                payload={
                    "query_type": "comparison",
                    "comparison_target": entities[1]
                }
            )
        
        return None
        
    def _parse_hypothetical_question(self, sent: Span) -> Optional[Signal]:
        """Parse hypothetical questions like 'What if X were Y?' or 'What would happen if X?'"""
        # Check for hypothetical keywords
        what_if = "what if" in sent.text.lower()
        would = any(t.lemma_ == "would" for t in sent)
        
        if not (what_if or would):
            return None
            
        # Extract the condition and question
        condition = {}
        question = {}
        
        # Simple pattern matching for "what if X were Y"
        what_if_match = re.search(r'what\s+if\s+([a-z\s]+)\s+(?:were|was)\s+([a-z\s]+)', sent.text.lower())
        if what_if_match:
            entity = what_if_match.group(1).strip()
            property_value = what_if_match.group(2).strip()
            
            condition = {
                "property": "state",
                "value": property_value
            }
            
            return Signal(
                origin=entity,
                purpose="QUERY",
                payload={
                    "query_type": "what_if",
                    "condition": condition
                }
            )
        
        return None
        
    def _parse_temporal_question(self, sent: Span) -> Optional[Signal]:
        """Parse temporal questions like 'When did X happen?' or 'What happened before X?'"""
        # Check for temporal question words
        has_when = any(t.lower_ == "when" for t in sent)
        temporal_words = ["before", "after", "during", "while"]
        has_temporal = any(word in sent.text.lower() for word in temporal_words)
        
        if not (has_when or has_temporal):
            return None
            
        # Extract the main entity
        subject = self._find_subject(sent)
        if not subject:
            return None
            
        # For "when" questions
        if has_when:
            return Signal(
                origin=subject.text,
                purpose="QUERY",
                payload={
                    "query_type": "when"
                }
            )
            
        # For before/after questions
        for word in temporal_words:
            if word in sent.text.lower():
                # Try to find the temporal reference
                pattern = rf'{word}\s+([a-z\s]+)'
                match = re.search(pattern, sent.text.lower())
                if match:
                    reference = match.group(1).strip()
                    return Signal(
                        origin=subject.text,
                        purpose="QUERY",
                        payload={
                            "temporal_relation": word,
                            "target": reference
                        }
                    )
        
        return None
