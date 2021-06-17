ENDPOINT_BASE = "https://api.pandascore.co/"
ENDPOINT_UPCOMING_MATCHES = "/matches/upcoming"
ENDPOINT_TEAMS = "/teams"

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
CONF_FILTER_TEAM = "filter_team"
CONF_MAX_UPCOMING_GAMES = "max_upcoming"
CONF_REFRESH_INTERVAL = "refresh_interval"

SENSOR_NAME_PREFIX = "Pandascore"
SENSOR_NAME_UPCOMING = "Upcoming Games"
UNIQUE_ID_PREFIX = "pandascore"
UNIQUE_ID_UPCOMING = "upcoming"
ATTR_MATCHES_LIST = "matches"
ATTR_MATCH_OPPONENTS = "opponents"
ATTR_MATCH_OPPONENT_NAME = "name"
ATTR_MATCH_OPPONENT_IMAGE_URL = "image_url"
ATTR_MATCH_BEGIN_AT = "begins_at"
ATTR_MATCH_STREAM_URL = "stream_url"
ATTR_MATCH_LEAGUE = "league"
ATTR_MATCH_TOURNAMENT = "tournament"
ATTR_MATCH_SERIES = "series"
