Home assistant support for TaiPower Fee

The method was provided by [Jason Lee](https://www.dcard.tw/@jas0n.1ee.com).

## Install

You can install component with [HACS](https://hacs.xyz/) custom repo: HACS > Integrations > 3 dots (upper top corner) > Custom repositories > URL: `tsunglung/TaiPowerFee` > Category: Integration

Or manually copy `taipower_fee` folder to `custom_components` folder in your config folder.

Then restart HA.

## Config

With GUI. Configuration > Integration > Add Integration > TaiPower Fee

If the integration is not in the list, you need to clear the browser cache.

# Setup

You need to grab a cookie and a csrf token.

**1. Basic steps for grabbing**

1. Open the development tools (use Google chrome/Microsoft Edge) [Crtl+Shift+I / F12]
2. Open the Network tab
3. Open the [TaiPower Fee Web site](https://ebpps2.taipower.com.tw/simplebill/simple-query-bill), Enter the Power Number and input Verification code.
4. Search for "post-simple-query-bill" (for me only one item shows up)
5. Go to "headers" -> "request headers"
6. copy the 56 characters like "SESSION=MDY3MTliZTQtYWMxNy00OTg1LTgyZGQtYTE5OTk1YjE5N2Y1" starting after "Cookie"  (mark with a mouse and copy to clipboard)
7. Go to "headers" -> "from data"
8. copy the 36 characters like "6c3b452f-7480-4b1d-ade0-1131561d63a1" starting after "\_csrf:"  (mark with a mouse and copy to clipboard)

![grabbing](grabbing.png)

**2. Please use the config flow of Home Assistant**

1. With GUI. Configuration > Integration > Add Integration > TaiPower Fee
   1. If the integration didn't show up in the list please REFRESH the page
2. Enter Power Number and Name in Chinese.
3. Paste the cookie and _csrf into the indicated field, all other fields are Required.

# Notice.
The cookie and csrf token will expired after hours. If you saw the https_result is 403, you need get the new cookie and csrf token again.
Then got to Configuration > Integration > TaiPower Fee > Options, enter the info of cookie and csrf token.