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
