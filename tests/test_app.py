# pylint: disable=missing-class-docstring
import logging
from pcg.app import App, AppRedisMixin, AppMongoMixin


DEFAULT_CONFIG = """
    app:
        name: test
        debug: true
    redis:
        uri: redis://localhost:6379/4
    mongodb:
        uri: mongodb://localhost:27017/ig
    logging:
        version: 1
        formatters:
            simple:
                format: '[%(app_uuid)s][%(levelname)s]:%(name)s : %(message)s'
        handlers:
            console:
                class: logging.StreamHandler
                level: DEBUG
                formatter: simple
                stream: ext://sys.stdout
        loggers:
            app.test:
                level: INFO
                handlers: [console]
                propagate: false
        root:
            level: ERROR
            handlers: [console]
"""


def test_app_basic():
    """Create default app, check if it's actually singleton"""

    class BasicApp(App):
        pass

    class AnotherApp(App):
        pass

    app = BasicApp()
    app_uuid = app.app_uuid
    assert isinstance(app, App)
    assert app_uuid is not None

    # class is singleton
    app = BasicApp()
    basic_uuid = app.app_uuid
    assert app.app_uuid == app_uuid

    app = AnotherApp()
    assert app.app_uuid != basic_uuid


def test_app_from_config(tmp_path):
    """Create app from config"""

    class BasicApp(App):
        pass

    config_file = tmp_path / "test_conf.yaml"
    config_file.write_text(DEFAULT_CONFIG)
    app = BasicApp.from_config(str(config_file))

    assert app.config["app"]["name"] == "test"
    assert "logging" in app.config


def test_app_setup_logging(tmp_path, caplog):
    """Check setup logging"""

    class BasicApp(App):
        pass

    config_file = tmp_path / "test_conf.yaml"
    config_file.write_text(DEFAULT_CONFIG)
    app = BasicApp.from_config(str(config_file))

    logger = logging.getLogger("app.test")
    app.setup_logging()
    print(logger.propagate)

    logger.info("Hello")
    logger.error("Wrong!")
    for record in caplog.records:
        assert str(app.app_uuid) in record.message


def test_app_mongodb_mixin(tmp_path):
    """Test app mixin - mongodb"""

    class BasicApp(App, AppMongoMixin):
        pass

    config_file = tmp_path / "test_conf.yaml"
    config_file.write_text(DEFAULT_CONFIG)
    app = BasicApp.from_config(str(config_file))

    assert app.config["app"]["name"] == "test"
