from src.api.use_cases import (
    CanonicalURLTopicVerificationUseCase
)


def test_CanonicalURLTopicVerificaitonUseCase():
    topic_base_url = 'http://tec-channel-api-au:9090/topic'
    uc = CanonicalURLTopicVerificationUseCase(topic_base_url)
    topic = 'http://tec-channel-api-au:9090/topic/aaaa.bbb.cc'
    topic_prefix = 'AU'
    uc.execute(topic, topic_prefix)
