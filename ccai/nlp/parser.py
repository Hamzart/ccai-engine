# ccai/nlp/parser.py

import spacy
from spacy.tokens import Token, Span
from typing import Optional

from ccai.core.models import Signal

class QueryParser:
    """
    Uses NLP (spaCy) to parse natural language questions into structured
    Signal objects for the reasoning core.
    """
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback for environments without the small English model.
            self.nlp = spacy.blank("en")
            self.nlp.add_pipe("sentencizer")
            # Add a light lemmatizer so simple rules still work
            self.nlp.add_pipe("lemmatizer", config={"mode": "rule"})
            self.nlp.initialize()

    def parse_question(self, text: str) -> Optional[Signal]:
        """
        Analyzes the dependency parse of a question to determine user intent.
        """
        cleaned = text.lower().strip()
        cleaned = cleaned.replace("what's", "what is").replace("whats", "what is")

        # Basic rule for definition-style questions to work without a parser
        for kw in ("define", "describe", "explain"):
            if cleaned.startswith(kw + " "):
                obj = cleaned[len(kw):].strip()
                if obj:
                    return Signal(origin=obj, purpose="QUERY", payload={"ask": "relation.is_a"})

        doc = self.nlp(cleaned.rstrip('?'))
        
        try:
            sent = next(doc.sents)
        except StopIteration:
            return None

        # --- Enhanced Intent Detection ---

        # 0. Definition-style questions
        if sent.root.lemma_ in {"define", "describe", "explain"}:
            obj = self._find_object(sent, sent.root, deps=("dobj", "attr", "pobj"))
            if obj:
                return Signal(origin=obj.text, purpose="QUERY", payload={"ask": "relation.is_a"})

        # 1. Check for Verification Intent (is, does, can)
        # This rule is now more specific: it only triggers if the sentence STARTS with an auxiliary verb.
        if sent[0].pos_ == "AUX":
            subject = self._find_subject(sent)
            root = sent.root

            if subject:
                # "is/are" questions
                if sent[0].lemma_ == 'be':
                    adj_obj = self._find_object(sent, root, deps=("acomp",))
                    if adj_obj:
                        return Signal(origin=subject.text, purpose='VERIFY', payload={'relation': 'has_property', 'target': adj_obj.text})
                    
                    noun_obj = self._find_object(sent, root, deps=("attr", "pobj", "dobj"))
                    if noun_obj:
                        return Signal(origin=subject.text, purpose='VERIFY', payload={'relation': 'is_a', 'target': noun_obj.text})

                # "does/do" questions
                if sent[0].lemma_ == 'do':
                    obj = self._find_object(sent, root, deps=("dobj",))
                    if root.lemma_ == 'have' and obj:
                        return Signal(origin=subject.text, purpose='VERIFY', payload={'relation': 'has_part', 'target': obj.text})
                    else:
                        return Signal(origin=subject.text, purpose='VERIFY', payload={'relation': 'can_do', 'target': root.lemma_})

                # "can" questions
                if sent[0].lemma_ == 'can':
                    return Signal(origin=subject.text, purpose='VERIFY', payload={'relation': 'can_do', 'target': root.lemma_})
        
        # 2. Check for "What" Query Intent
        if "what" in [t.lower_ for t in sent]:
            subject = self._find_subject(sent)
            if not subject: subject = sent.root

            if "is" in [t.text for t in sent] or "are" in [t.text for t in sent]:
                return Signal(origin=subject.text, purpose="QUERY", payload={"ask": "relation.is_a"})
            if "have" in [t.lemma_ for t in sent] or "properties" in sent.text:
                return Signal(origin=subject.text, purpose="QUERY", payload={"ask_relation": "has_part"})
            # NEW: Handles "what does X do?"
            if ("can" in [t.text for t in sent] or "does" in [t.text for t in sent]) and "do" in [t.lemma_ for t in sent]:
                return Signal(origin=subject.text, purpose="QUERY", payload={"ask_relation": "can_do"})
            if "used for" in sent.text:
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
