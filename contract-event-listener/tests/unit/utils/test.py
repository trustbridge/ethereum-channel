from src.utils.jmespath_json_template import JMESPathJSONTemplate


def test_jmespath_json_tempalte():
    data = {
        "receiver": {
            "messages": [
                {
                    "text": "Hello",
                    "status": "delivered"
                },
                {
                    "text": "world",
                    "status": "delivered"
                },
                {
                    "text": "!",
                    "status": "pending"
                }
            ]
        }
    }
    json_template = {
        "messages": {
            "first": "receiver.messages[0].text",
            "last": "receiver.messages[-1].text"
        },
        "statuses": [{"status": "receiver.messages[0].status"}, {"status": "receiver.messages[-1].status"}]
    }
    result = JMESPathJSONTemplate(json_template).render(data)
    assert result == {
        "messages": {
            "first": "Hello",
            "last": "!"
        },
        "statuses": [{"status": "delivered"}, {"status": "pending"}]
    }

    result = JMESPathJSONTemplate({"messages": "receiver.messages[].text"}).render(data)
    assert result == {"messages": ["Hello", "world", "!"]}

    assert JMESPathJSONTemplate("receiver.messages[1].text").render(data) == "world"
