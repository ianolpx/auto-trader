
from pybit.unified_trading import HTTP
from settings import settings
import math


class BybitHandler():
    def __init__(self):
        self.session = HTTP(
            testnet=False,
            api_key=settings.bybit_api_key,
            api_secret=settings.bybit_secret_key
        )

    def truncate(self, number, digits) -> float:
        nbDecimals = len(str(number).split('.')[1])
        if nbDecimals <= digits:
            return 0.0
        stepper = 10.0 ** digits
        return math.trunc(stepper * number) / stepper

    def get_available_budget_usdt(self) -> float:
        result = self.session.get_wallet_balance(
            accountType='UNIFIED',
            coin='USDT')['result']
        coin = result['list'][0]['coin'][0]
        return self.truncate(float(coin['walletBalance']) * 0.8, 2)

    def buy_eth(self):
        res = self.session.place_order(
            category="spot",
            symbol="ETHUSDT",
            side="Buy",
            orderType="Market",
            qty=self.get_available_budget_usdt()
        )
        return res

    def get_decimal(self, _value):
        value = str(_value)
        if '.' in value:
            return len(value.split('.')[1])
        else:
            return 0

    def get_spot_btcusdt_decimal(self) -> int:
        result = self.session.get_orderbook(
                category="spot",
                symbol='ETHUSDT')['result']
        decimal_a = self.get_decimal(result['a'][0][1])
        decimal_b = self.get_decimal(result['b'][0][1])
        return max(decimal_a, decimal_b)

    def get_sellable_quantity_eth(self) -> float:
        result = self.session.get_wallet_balance(
            accountType='UNIFIED',
            coin='ETH')['result']
        coin_info = result['list'][0]['coin'][0]
        # decimal = self.get_spot_btcusdt_decimal()
        decimal = 5
        return self.truncate(float(coin_info['walletBalance']), decimal)

    def sell_eth(self):
        res = self.session.place_order(
            category="spot",
            symbol="ETHUSDT",
            side="Sell",
            orderType="Market",
            qty=self.get_sellable_quantity_eth()
        )
        return res


# python -m handlers.bybit
if __name__ == "__main__":
    BH = BybitHandler()
    print(BH.get_available_budget_usdt())
