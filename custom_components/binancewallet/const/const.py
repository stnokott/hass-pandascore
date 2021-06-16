import enum
import logging

ENDPOINT_BASE = "https://api.pandascore.co"
ENDPOINT_UPCOMING_MATCHES = "/matches/upcoming"

CONF_API_KEY = "api_key"
CONF_GAME = "game"
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


class EnumGames(enum.Enum):
    CODMW = "codmw"
    CSGO = "csgo"
    DOTA2 = "dota2"
    LOL = "lol"
    PUBG = "pubg"
    OVERWATCH = "ow"
    ROCKETLEAGUE = "rl"
    RAINBOW6 = "r6siege"
    FIFA = "fifa"
    VALORANT = "valorant"