from pytest import fixture

from web3_reactor.services.config import ConfigScope


@fixture
def config():
    return ConfigScope("test")


class TestConfig:

    def test_create(self, config):
        assert config.__name__ == "test.yaml"

    def test_set(self, config):
        config["test"] = "test_set"
        assert config.get("test") == "test_set"

    def test_save(self, config):
        config.save()

    def test_reload(self, config):
        config.reload()
        assert config.get("test") == "test_set"
