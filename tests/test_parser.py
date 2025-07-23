import spacy
from ccai.nlp.parser import QueryParser


def test_define_question(monkeypatch):
    def raise_oserror(name, *args, **kwargs):
        raise OSError("model missing")
    monkeypatch.setattr(spacy, "load", raise_oserror)
    parser = QueryParser()
    sig = parser.parse_question("define car")
    assert sig is not None
    assert sig.purpose == "QUERY"
    assert sig.payload["ask"] == "relation.is_a"
    assert sig.origin == "car"


