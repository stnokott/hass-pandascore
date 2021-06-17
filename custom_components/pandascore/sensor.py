"""
Retrieves esports data from Pandascore

TODO:
- Config flow
"""
import logging
import urllib.error

import voluptuous as vol

from .const.const import (
    CONF_API_KEY,
    CONF_GAME,
    CONF_REFRESH_INTERVAL,
    ENDPOINT_BASE,
    SENSOR_NAME_PREFIX,
    ATTR_MATCHES_LIST,
    ENDPOINT_UPCOMING_MATCHES,
    UNIQUE_ID_PREFIX,
    UNIQUE_ID_UPCOMING,
    SENSOR_NAME_UPCOMING,
    CONF_MAX_UPCOMING_GAMES,
    ATTR_MATCH_BEGIN_AT,
    ATTR_MATCH_STREAM_URL,
    CONF_SUPPORTED_GAMES,
    ATTR_MATCH_LEAGUE,
    ATTR_MATCH_TOURNAMENT,
    CONF_FILTER_TEAM,
    ENDPOINT_TEAMS,
    ATTR_MATCH_SERIES,
    ATTR_MATCH_OPPONENTS,
    ATTR_MATCH_OPPONENT_NAME,
    ATTR_MATCH_OPPONENT_IMAGE_URL,
)

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity

from datetime import timedelta
from typing import Optional, List

import requests

LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Required(CONF_GAME): vol.In(CONF_SUPPORTED_GAMES.keys()),
        vol.Optional(CONF_FILTER_TEAM, default=""): cv.string,
        vol.Optional(CONF_MAX_UPCOMING_GAMES, default=5): cv.positive_int,
        vol.Optional(CONF_REFRESH_INTERVAL, default=60): cv.positive_int,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    LOGGER.debug("Setting up sensor")

    api_key = config.get(CONF_API_KEY)
    game = config.get(CONF_GAME)
    filter_team = config.get(CONF_FILTER_TEAM)
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
                filter_team,
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
        self,
        api_key,
        game,
        filter_team_raw,
        max_upcoming,
        filter_opponent_id,
        refresh_interval,
    ):
        self.update = Throttle(timedelta(minutes=refresh_interval))(self._update)
        self._unique_id = f"{UNIQUE_ID_PREFIX}_{game}_{UNIQUE_ID_UPCOMING}"
        self._name = (
            f"{SENSOR_NAME_PREFIX} {CONF_SUPPORTED_GAMES[game]} {SENSOR_NAME_UPCOMING}"
        )
        self._upcoming_games: List[UpcomingGame] = []
        self._state: Optional[int] = None
        self._api_manager = APIManager(api_key, game, filter_team_raw)
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
            ATTR_MATCHES_LIST: [
                {
                    ATTR_MATCH_OPPONENTS: [
                        {
                            ATTR_MATCH_OPPONENT_NAME: opponent.name,
                            ATTR_MATCH_OPPONENT_IMAGE_URL: opponent.image_url,
                        }
                        for opponent in game.opponents
                    ],
                    ATTR_MATCH_LEAGUE: game.league,
                    ATTR_MATCH_TOURNAMENT: game.tournament,
                    ATTR_MATCH_SERIES: game.series,
                    ATTR_MATCH_BEGIN_AT: game.begin_at,
                    ATTR_MATCH_STREAM_URL: game.stream_url,
                }
                for game in self._upcoming_games
            ]
        }

    def _update(self):
        self._upcoming_games = self._api_manager.get_upcoming_games(self._max_upcoming)
        self._state = len(self._upcoming_games)


class Team:
    def __init__(self, name: str, image_url: str):
        self.name = name
        self.image_url = image_url


class UpcomingGame:
    def __init__(
        self,
        opponents: List[Team],
        league: str,
        tournament: str,
        series: str,
        begin_at: str,
        stream_url: str,
    ):
        self.opponents = opponents
        self.league = league
        self.tournament = tournament
        self.series = series
        self.begin_at = begin_at
        self.stream_url = stream_url


class APIManager:
    def __init__(self, api_key: str, game: str, filter_team_raw: str):
        self._api_key = api_key
        self._game = game
        self._filter_team_raw = filter_team_raw
        self._filter_team_id: Optional[int] = None

        self._headers = {"Authorization": f"Bearer {self._api_key}"}
        self._remaining_calls = 1000

    def _execute_request(
        self, endpoint: str, per_page: int, additional_params: dict
    ) -> Optional[dict]:
        if self._remaining_calls == 0:
            LOGGER.warning("API call limit exceeded, please try again in an hour.")
            return None

        url = ENDPOINT_BASE + self._game + endpoint
        params = {"per_page": per_page}
        params.update(additional_params)

        r = requests.get(url, params, headers=self._headers)

        if "X-Rate-Limit-Remaining" in r.headers:
            self._remaining_calls = int(r.headers["X-Rate-Limit-Remaining"])
            LOGGER.debug(f"Remaining calls: {self._remaining_calls}")

        if r.status_code != 200:
            LOGGER.warning(
                f"Unsuccessful HTTP request to {url}: {r.status_code} -> {r.text}"
            )
            return None
        else:
            return r.json()

    def get_upcoming_games(self, max_count: int) -> List[UpcomingGame]:
        additional_params = {}

        if len(self._filter_team_raw) > 0:
            if self._filter_team_id is None:
                self._filter_team_id = self._resolve_team_name(self._filter_team_raw)
            if self._filter_team_id is None:
                LOGGER.warning("Team name unresolved, ignoring filter")
            else:
                additional_params["filter[opponent_id]"] = self._filter_team_id

        result = []
        response = self._execute_request(
            ENDPOINT_UPCOMING_MATCHES, max_count, additional_params
        )
        if response is None:
            return result
        try:
            for game in response:
                result.append(
                    UpcomingGame(
                        [
                            Team(
                                opponent["opponent"]["name"],
                                opponent["opponent"]["image_url"],
                            )
                            for opponent in game["opponents"]
                        ],
                        game["league"]["name"],
                        game["tournament"]["name"],
                        game["serie"]["name"],
                        game["begin_at"],
                        game["official_stream_url"],
                    )
                )
        except KeyError as e:
            LOGGER.warning(f"Required attribute missing in response JSON: {e}")
        return result

    def _resolve_team_name(self, team_name: str) -> Optional[int]:
        additional_params = {"search[name]": team_name}
        response = self._execute_request(ENDPOINT_TEAMS, 1, additional_params)
        if response is None or len(response) == 0:
            LOGGER.warning(f"Could not resolve team name <{team_name}>")
            return None
        try:
            return response[0]["id"]
        except KeyError as e:
            LOGGER.warning(f"Team ID for <{team_name}> not found ({e})")
            return None
