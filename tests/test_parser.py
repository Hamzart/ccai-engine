from ccai.nlp.parser import QueryParser

def test_define_question():
    parser = QueryParser()
    sig = parser.parse_question("define car")
    assert sig is not None
    assert sig.purpose == "QUERY"
    assert sig.payload["ask"] == "relation.is_a"
    assert sig.origin == "car"

