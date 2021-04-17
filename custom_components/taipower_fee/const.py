"""Constants of the TaiPower Fee component."""

DEFAULT_NAME = "TaiPower Fee"
DOMAIN = "taipower_fee"
DOMAINS = ["sensor"]
DATA_KEY = "sensor.taipower_fee"

ATTR_BILLING_MONTH = "billing_month"
ATTR_BILLING_DATE = "billing_date"
ATTR_PAYMENT = "payment"
ATTR_POWER_CONSUMPTION = "power_consumption"
ATTR_COLLECTION_DATE = "collection_date"
ATTR_BILL_AMOUNT = "billing_amount"
ATTR_HTTPS_RESULT = "https_result"
ATTR_LIST = [
    ATTR_BILLING_MONTH,
    ATTR_BILLING_DATE,
    ATTR_PAYMENT,
    ATTR_POWER_CONSUMPTION,
    ATTR_COLLECTION_DATE,
    ATTR_BILL_AMOUNT,
    ATTR_HTTPS_RESULT
]

CONF_CUSTNO = "cust_no"
CONF_COOKIE = "cookie"
CONF_CSRF = "csrf"
ATTRIBUTION = "Powered by TaiPower Fee Data"

HA_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36 OPR/38.0.2220.41"
BASE_URL = 'https://ebpps2.taipower.com.tw/simplebill/post-simple-query-billdetail'

REQUEST_TIMEOUT = 10  # seconds
