"""
Retrieves esports data from Pandascore

TODO:
- Config flow
"""
import urllib.error

import voluptuous as vol

from .const.const import (
    LOGGER,
    CONF_API_KEY,
    CONF_GAME,
    CONF_REFRESH_INTERVAL,
    ENDPOINT_BASE,
    SENSOR_NAME_PREFIX,
    ATTR_GAMES_LIST,
    ENDPOINT_UPCOMING_MATCHES,
    UNIQUE_ID_PREFIX,
    UNIQUE_ID_UPCOMING,
    SENSOR_NAME_UPCOMING,
    CONF_MAX_UPCOMING_GAMES,
    ATTR_GAME_NAME,
    ATTR_GAME_BEGIN_AT,
    ATTR_GAME_STREAM_URL,
    CONF_SUPPORTED_GAMES,
)

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity

from datetime import timedelta
import json
from typing import Optional, List
from urllib.parse import urljoin

import requests

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Required(CONF_GAME): vol.In(CONF_SUPPORTED_GAMES.keys()),
        vol.Optional(CONF_MAX_UPCOMING_GAMES, default=5): cv.positive_int,
        vol.Optional(CONF_REFRESH_INTERVAL, default=60): cv.positive_int,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    LOGGER.debug("Setting up sensor")

    api_key = config.get(CONF_API_KEY)
    game = config.get(CONF_GAME)
    max_upcoming = int(config.get(CONF_MAX_UPCOMING_GAMES))
    if max_upcoming > 100:
        LOGGER.warning(
            f"{CONF_MAX_UPCOMING_GAMES} set to {max_upcoming}, maximum 100 allowed!"
        )
        max_upcoming = 100
    filter_opponent_id = "126940"
    refresh_interval = int(config.get(CONF_REFRESH_INTERVAL))

    entities = []

    try:
        entities.append(
            UpcomingGamesSensor(
                api_key,
                game,
                max_upcoming,
                filter_opponent_id,
                refresh_interval,
            )
        )
    except urllib.error.HTTPError as e:
        LOGGER.error(e.reason)
        return False

    add_entities(entities)


class UpcomingGamesSensor(Entity):
    def __init__(
        self, api_key, game, max_upcoming, filter_opponent_id, refresh_interval
    ):
        self.update = Throttle(timedelta(minutes=refresh_interval))(self._update)
        # UNIQUE_ID
        self._unique_id = f"{UNIQUE_ID_PREFIX}_{game}_{UNIQUE_ID_UPCOMING}"
        # FRIENDLY NAME
        self._name = (
            f"{SENSOR_NAME_PREFIX} {CONF_SUPPORTED_GAMES[game]} {SENSOR_NAME_UPCOMING}"
        )
        self._upcoming_games: List[UpcomingGame] = []
        self._state: Optional[int] = None
        self._wallet = APIManager(api_key, game)
        self._max_upcoming = max_upcoming
        self._filter_opponent_id = filter_opponent_id

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return "mdi:controller-classic"

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        return {
            ATTR_GAMES_LIST: [
                {
                    ATTR_GAME_NAME: game.name,
                    ATTR_GAME_BEGIN_AT: game.begin_at,
                    ATTR_GAME_STREAM_URL: game.stream_url,
                }
                for game in self._upcoming_games
            ]
        }

    def _update(self):
        self._upcoming_games = self._wallet.get_upcoming_games(
            self._filter_opponent_id, self._max_upcoming
        )
        self._state = len(self._upcoming_games)


class UpcomingGame:
    def __init__(self, name: str, begin_at: str, stream_url: str):
        self.name = name
        self.begin_at = begin_at
        self.stream_url = stream_url


class APIManager:
    def __init__(self, api_key: str, game: str):
        self._api_key = api_key
        self._game = game

        self._headers = {"Authorization": f"Bearer {self._api_key}"}

    def get_upcoming_games(
        self, filter_opponent_id: str, max_count: int
    ) -> List[UpcomingGame]:
        url = ENDPOINT_BASE + self._game + ENDPOINT_UPCOMING_MATCHES

        params = {"per_page": max_count}
        if len(filter_opponent_id) > 0:
            params["filter[opponent_id]"] = filter_opponent_id

        r = requests.get(url, params, headers=self._headers)
        if r.status_code != 200:
            LOGGER.warning(f"Unsuccessful HTTP request: {r.status_code} -> {r.text}")
            return []
        else:
            LOGGER.debug(f"Remaining calls: {r.headers['X-Rate-Limit-Remaining']}")
            result = []
            try:
                response_json = r.json()
                for game in response_json:
                    result.append(
                        UpcomingGame(
                            game["name"], game["begin_at"], game["official_stream_url"]
                        )
                    )
            except json.JSONDecodeError as e1:
                LOGGER.warning(f"Could not parse response as JSON: {e1}")
            except KeyError as e2:
                LOGGER.warning(f"Required attribute missing in response JSON: {e2}")
            return result
