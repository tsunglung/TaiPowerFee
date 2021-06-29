"""Config flow to configure TaiPower Fee component."""
from collections import OrderedDict
from typing import Optional
import voluptuous as vol

from homeassistant.config_entries import (
    CONN_CLASS_LOCAL_PUSH,
    ConfigFlow,
    OptionsFlow,
    ConfigEntry
)
from homeassistant.const import CONF_NAME, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN, DEFAULT_NAME, CONF_CUSTNO, CONF_COOKIE, CONF_CSRF


class LineBotFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a TaiPower Fee config flow."""

    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_LOCAL_PUSH

    def __init__(self):
        """Initialize flow."""
        self._username: Optional[str] = None
        self._cust_no: Optional[str] = None
        self._csrf: Optional[str] = None
        self._cookie: Optional[str] = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        """ get option flow """
        return OptionsFlowHandler(config_entry)

    async def async_step_user(
        self,
        user_input: Optional[ConfigType] = None,
        error: Optional[str] = None
    ):  # pylint: disable=arguments-differ
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self._set_user_input(user_input)
            self._name = user_input.get(CONF_CUSTNO)
            unique_id = self._cust_no
            await self.async_set_unique_id(unique_id)
            return self._async_get_entry()

        fields = OrderedDict()
        fields[vol.Required(CONF_USERNAME,
                            default=self._username or vol.UNDEFINED)] = str
        fields[vol.Required(CONF_CUSTNO,
                            default=self._cust_no or vol.UNDEFINED)] = str
        fields[vol.Required(CONF_COOKIE,
                            default=self._cookie or vol.UNDEFINED)] = str
        fields[vol.Required(CONF_CSRF,
                            default=self._csrf or vol.UNDEFINED)] = str
        self._name = self._username
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(fields),
            errors={'base': error} if error else None
        )

    @property
    def _name(self):
        # pylint: disable=no-member
        # https://github.com/PyCQA/pylint/issues/3167
        return self.context.get(CONF_NAME)

    @_name.setter
    def _name(self, value):
        # pylint: disable=no-member
        # https://github.com/PyCQA/pylint/issues/3167
        self.context[CONF_NAME] = value
        self.context["title_placeholders"] = {"name": self._name}

    def _set_user_input(self, user_input):
        if user_input is None:
            return
        self._username = user_input.get(CONF_USERNAME, "")
        self._cust_no = user_input.get(CONF_CUSTNO, "")
        self._cookie = user_input.get(CONF_COOKIE, "")
        self._csrf = user_input.get(CONF_CSRF, "")

    @callback
    def _async_get_entry(self):
        return self.async_create_entry(
            title=self._name,
            data={
                CONF_USERNAME: self._username,
                CONF_CUSTNO: self._cust_no,
                CONF_COOKIE: self._cookie,
                CONF_CSRF: self._csrf,
            },
        )


class OptionsFlowHandler(OptionsFlow):
    # pylint: disable=too-few-public-methods
    """Handle options flow changes."""
    _username = None
    _cust_no = None
    _cookie = None
    _csrf = None

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage options."""
        if user_input is not None:
            self._username = user_input.get(CONF_USERNAME)
            self._cust_no = user_input.get(CONF_CUSTNO)
            self._cookie = user_input.get(CONF_COOKIE)
            self._csrf = user_input.get(CONF_CSRF)
            return self.async_create_entry(
                title='',
                data={
                    CONF_USERNAME: self._username,
                    CONF_CUSTNO: self._cust_no,
                    CONF_COOKIE: self._cookie,
                    CONF_CSRF: self._csrf,
                },
            )
        self._username = self.config_entry.options.get(CONF_USERNAME, '')
        self._cust_no = self.config_entry.options.get(CONF_CUSTNO, '')
        self._cookie = self.config_entry.options.get(CONF_COOKIE, '')
        self._csrf = self.config_entry.options.get(CONF_CSRF, '')

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME, default=self._username): str,
                    vol.Required(CONF_CUSTNO, default=self._cust_no): str,
                    vol.Required(CONF_COOKIE, default=self._cookie): str,
                    vol.Required(CONF_CSRF, default=self._csrf): str
                }
            ),
        )
