from src.components.config import load_config


def test_empty_output_add_timestamp_env_disables_timestamps(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        'target_url: "https://example.com"\n'
        'output_csv_path: "data/leaderboard.csv"\n'
        "output_add_timestamp: true\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("OUTPUT_ADD_TIMESTAMP", "")

    config = load_config(str(config_path))

    assert config["output_add_timestamp"] is False


def test_load_config_defaults_locale_settings(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        'target_url: "https://example.com"\n'
        'output_csv_path: "data/leaderboard.csv"\n'
        "output_add_timestamp: true\n",
        encoding="utf-8",
    )

    config = load_config(str(config_path))

    assert config["output_localize_numbers"] is True
    assert config["output_locale"] == "el_GR"


def test_output_locale_env_overrides_config(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        'target_url: "https://example.com"\n'
        'output_csv_path: "data/leaderboard.csv"\n'
        "output_localize_numbers: false\n"
        'output_locale: "fr_FR"\n',
        encoding="utf-8",
    )

    monkeypatch.setenv("OUTPUT_LOCALIZE_NUMBERS", "true")
    monkeypatch.setenv("OUTPUT_LOCALE", "de_DE")

    config = load_config(str(config_path))

    assert config["output_localize_numbers"] is True
    assert config["output_locale"] == "de_DE"
