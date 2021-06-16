## Home Assistant sensor component for Pandascore Esports API 

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
### Powered by Pandascore API

#### Provides information about upcoming esports games from Pandascore

### Features
- Count of total upcoming games as value
- List of upcoming games as attribute

#### Attributes
- `games[]`: List of upcoming games
  - `name`: Name of match, e.g. "G2 vs Disrupt"
  - `begin_at`: Expected match start in ISO 8601 format
  - `stream_url`: URL of stream (e.g. Twitch) for this game

### Configuration
- First, create an account at [Pandascore](https://app.pandascore.co/signup) (the free tier allows for up to 1000 calls per hour which should suffice in most cases).
- Copy your **access token** from your [dashboard](https://app.pandascore.co/dashboard/main):
- Use your `secrets.yaml` to store the key (see [this guide](https://www.home-assistant.io/docs/configuration/secrets/)).
  You can also paste it as plain-text in the `configuration.yaml` though this is **not recommended**.
- Create a sensor entry in your `configuration.yaml` like this:
```Configuration.yaml:
  sensor:
    - platform: pandascore
      api_key: !secret pandascore_api_key  (required)
      game: "r6siege"                      (required, see below for supported values)
      max_upcoming: 5                      (optional, default=5, amount of upcoming games to retrieve per call, max. 100)
      refresh_interval: 60                 (optional, default=60, refresh interval in minutes)
```

### Supported games
|Name|Configuration value|
|-----------------|-----------|
|Call of Duty: MW |`codmw`    |
|CS:GO            |`csgo`     |
|DOTA 2           |`dota2`    |
|LoL              |`lol`      |
|PUBG             |`pubg`     |
|Overwatch        |`overwatch`|
|RocketLeague     |`rl`       |
|Rainbow Six Siege|`r6siege`  |
|FIFA             |`fifa`     |
|Valorant         |`valorant` |