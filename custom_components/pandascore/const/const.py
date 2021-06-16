import logging

ENDPOINT_BASE = "https://api.pandascore.co/"
ENDPOINT_UPCOMING_MATCHES = "/matches/upcoming"

CONF_API_KEY = "api_key"
CONF_GAME = "game"
CONF_SUPPORTED_GAMES = {
    "codmw": "Call of Duty: MW",
    "csgo": "CS:GO",
    "dota2": "DOTA 2",
    "lol": "LoL",
    "pubg": "PUBG",
    "ow": "Overwatch",
    "rl": "RocketLeague",
    "r6siege": "Rainbow Six Siege",
    "fifa": "FIFA",
    "valorant": "Valorant",
}
CONF_MAX_UPCOMING_GAMES = "max_upcoming"
CONF_REFRESH_INTERVAL = "refresh_interval"

SENSOR_NAME_PREFIX = "Pandascore"
SENSOR_NAME_UPCOMING = "Upcoming Games"
UNIQUE_ID_PREFIX = "pandascore"
UNIQUE_ID_UPCOMING = "upcoming"
ATTR_GAMES_LIST = "games"
ATTR_GAME_NAME = "name"
ATTR_GAME_BEGIN_AT = "begins_at"
ATTR_GAME_STREAM_URL = "stream_url"

LOGGER = logging.getLogger(__name__)
