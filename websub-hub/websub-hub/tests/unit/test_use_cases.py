from src.use_cases import DeliverCallbackUseCase


def test_deliver_callback_get_retry_time():
    attempts = [0, 0, 0, 0]
    for i in range(0, 1000):
        attempts[1] = DeliverCallbackUseCase._get_retry_time(1)
        attempts[2] = DeliverCallbackUseCase._get_retry_time(2)
        attempts[3] = DeliverCallbackUseCase._get_retry_time(3)
        assert 8 <= attempts[1] <= 16
        assert 16 <= attempts[2] <= 32
        assert 32 <= attempts[3] <= 64
        assert attempts[1] < attempts[2] < attempts[3]
