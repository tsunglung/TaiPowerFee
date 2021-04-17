"""Support for the TaiPower Fee.

https://ebpps2.taipower.com.tw/simplebill/simple-query-bill
"""
import logging
from typing import Callable
from datetime import timedelta

from aiohttp.hdrs import USER_AGENT
import requests
from bs4 import BeautifulSoup

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity
from homeassistant.util import Throttle
import homeassistant.util.dt as dt_util
from homeassistant.helpers.event import track_point_in_time
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    CONF_USERNAME,
    CURRENCY_DOLLAR,
    HTTP_OK,
    HTTP_FORBIDDEN,
    HTTP_NOT_FOUND,
)
from .const import (
    ATTRIBUTION,
    ATTR_BILLING_MONTH,
    ATTR_BILLING_DATE,
    ATTR_PAYMENT,
    ATTR_POWER_CONSUMPTION,
    ATTR_COLLECTION_DATE,
    ATTR_BILL_AMOUNT,
    ATTR_HTTPS_RESULT,
    ATTR_LIST,
    BASE_URL,
    CONF_CUSTNO,
    CONF_CSRF,
    CONF_COOKIE,
    DATA_KEY,
    HA_USER_AGENT,
    REQUEST_TIMEOUT
)

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_FORCED_UPDATES = timedelta(minutes=15)
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=45)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_devices: Callable
) -> None:
    """Set up the TaiPower Fee Sensor from config."""
    _LOGGER.error("setup_entry")
    if DATA_KEY not in hass.data:
        hass.data[DATA_KEY] = {}

    if config.data.get(CONF_USERNAME, None):
        username = config.data[CONF_USERNAME]
        cust_no = config.data[CONF_CUSTNO]
        csrf = config.data[CONF_CSRF]
        cookie = config.data[CONF_COOKIE]
    else:
        username = config.options[CONF_USERNAME]
        cust_no = config.options[CONF_CUSTNO]
        csrf = config.options[CONF_CSRF]
        cookie = config.options[CONF_COOKIE]

    data = TaiPowerFeeData(username, cust_no, csrf, cookie)
    device = TaiPowerFeeSensor(data, cust_no)

    hass.data[DATA_KEY][config.entry_id] = device
    async_add_devices([device], update_before_add=True)


class TaiPowerFeeData():
    """Class for handling the data retrieval."""

    def __init__(self, username, cust_no, csrf, cookie):
        """Initialize the data object."""
        self.data = {}
        self._username = username
        self._custno = cust_no
        self._cookie = cookie
        self._csrf = csrf
        self.uri = BASE_URL

    def update_no_throttle(self):
        """Get the data for a specific email."""
        self.update(no_throttle=True)

    @Throttle(MIN_TIME_BETWEEN_UPDATES, MIN_TIME_BETWEEN_FORCED_UPDATES)
    def update(self, **kwargs):
        """Get the latest data for cust no from REST service."""
        headers = {USER_AGENT: HA_USER_AGENT, "Cookie": self._cookie}
        payload = {
            "_csrf": self._csrf,
            "custNo": self._custno,
            "billName": self._username,
            "Search": "\u67e5\u8a62\u660e\u7d30"}

        try:
            req = requests.post(
                self.uri,
                headers=headers,
                data=payload,
                timeout=REQUEST_TIMEOUT)

        except requests.exceptions.RequestException:
            _LOGGER.error("Failed fetching data for %s", self._custno)
            return

        if req.status_code == HTTP_OK:
            soup = BeautifulSoup(req.text, 'html.parser')
            billdetail = soup.find(id="billDaetailArea")
            results = billdetail.find_all(["th", "td"])
            results2 = [i.string for i in results]
            self.data[self._custno] = dict(zip(results2[::2], results2[1::2]))
            self.data[self._custno]['result'] = HTTP_OK

        elif req.status_code == HTTP_NOT_FOUND:
            self.data[self._custno] = []
            self.data[self._custno]['result'] = HTTP_NOT_FOUND

        else:
            info = ""
            if req.status_code == HTTP_FORBIDDEN:
                info = "CSRF token or Cookie is expired"
            _LOGGER.error(
                "Failed fetching data for %s (HTTP Status_code = %d). %s",
                self._custno,
                req.status_code,
                info
            )
            self.data = {}
            self.data[self._custno]['result'] = req.status_code


class TaiPowerFeeSensor(SensorEntity):
    """Implementation of a TaiPower Fee sensor."""

    def __init__(self, data, cust_no):
        """Initialize the sensor."""
        self._state = None
        self._data = data
        self._attributes = {}
        self._attr_value = {}
        self._name = "taipower_fee_{}".format(cust_no)
        self._custno = cust_no

        self.uri = BASE_URL
        for i in ATTR_LIST:
            self._attr_value[i] = None
        self._data.data[self._custno] = {}
        self._data.data[self._custno]['result'] = None

    @property
    def unique_id(self):
        """Return an unique ID."""
        return self._name

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return "mdi:currency-twd"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return CURRENCY_DOLLAR

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        self._attributes[ATTR_ATTRIBUTION] = ATTRIBUTION
        for i in ATTR_LIST:
            self._attributes[i] = self._attr_value[i]
        return self._attributes

    async def async_added_to_hass(self):
        """Get initial data."""
        # To make sure we get initial data for the sensors ignoring the normal
        # throttle of 7 days but using an update throttle of 1 day
        self.hass.async_add_executor_job(self.update_nothrottle)

    def update_nothrottle(self, dummy=None):
        """Update sensor without throttle."""
        self._data.update_no_throttle()

        # Schedule a forced update 1 day in the future if the update above
        # returned no data for this sensors power number.
        if len(self._data.data) < 2:
            track_point_in_time(
                self.hass,
                self.update_nothrottle,
                dt_util.now() + MIN_TIME_BETWEEN_FORCED_UPDATES,
            )
            return

        self.schedule_update_ha_state()

    async def async_update(self):
        """Update state."""
#        self._data.update()
        self.hass.async_add_executor_job(self._data.update)
        if self._custno in self._data.data:
            for i, j in self._data.data[self._custno].items():
                if "\u61c9\u7e73\u7e3d\u91d1\u984d\uff1a" in i:
                    self._state = int(''.join(k for k in j if k.isdigit()))
                    self._attr_value[ATTR_BILL_AMOUNT] = j
                if "\u5e33\u55ae\u6708\u4efd\uff1a" in i:
                    self._attr_value[ATTR_BILLING_MONTH] = j
                if "\u6536\u8cbb\u65e5\uff1a" in i:
                    self._attr_value[ATTR_BILLING_DATE] = j
                if "\u7e73\u8cbb\u671f\u9650\uff1a" in i:
                    self._attr_value[ATTR_PAYMENT] = j
                if "\u7528\u96fb\u5ea6\u6578\uff1a" in i:
                    self._attr_value[ATTR_POWER_CONSUMPTION] = j
                if "\u4ee3\u6536\u622a\u6b62\u65e5\uff1a" in i:
                    self._attr_value[ATTR_COLLECTION_DATE] = j
            self._attr_value[ATTR_HTTPS_RESULT] = self._data.data[
                self._custno]['result']
            if self._attr_value[ATTR_HTTPS_RESULT] == HTTP_FORBIDDEN:
                self._state = None
