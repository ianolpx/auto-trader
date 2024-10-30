from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import f1_score, accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from ta import add_all_ta_features

import pandas as pd
import ccxt.async_support as ccxt
import logging
import asyncio
import time

class AlgoHandler():
    def run(self):
        logging.info("Hello from AlgoHandler")

    async def get_data(self, symbol, timeframe):
        bybit = ccxt.bybit()

        async with bybit:
            # etc_ohlcv = await bybit.fetch_ohlcv('ETH/USDT', '1d')
            etc_ohlcv = await bybit.fetch_ohlcv(symbol, timeframe)
            df = pd.DataFrame(
                etc_ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['Datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df

    async def get_insight(self):
        df = await self.get_data('ETH/USDT', '1d')
        df = df[['Datetime', 'open', 'high', 'low', 'close', 'volume']]
        df.set_index('Datetime', inplace=True)
        _all_data = add_all_ta_features(
            df,
            open="open", high="high", low="low", close="close", volume="volume"
        )

        _all_data = _all_data.drop(
            ['trend_psar_down', 'trend_psar_up'], axis=1)
        _all_data.dropna(inplace=True)
        _all_data['target'] = _all_data['close'].shift(-5)
        current_x = _all_data.iloc[-1].drop('target')
        _all_data.dropna(inplace=True)

        X = _all_data.drop('target', axis=1)
        y = _all_data['target']

        k_best = SelectKBest(f_classif, k=10)
        k_best.fit(X, y)
        X.columns[k_best.get_support()]

        best_features = X.columns[k_best.get_support()]

        X_new = X[best_features]

        new_y = []
        for close, target in zip(_all_data['close'], y):
            if target > close * 1.02:
                new_y.append(1)
            else:
                new_y.append(0)

        classifier = RandomForestClassifier()

        # val = cross_val_score(classifier, X_new, new_y, cv=5)
        # print(val)

        X_train, X_test, y_train, y_test = train_test_split(
            X_new, new_y, test_size=0.2, random_state=42)
        classifier.fit(X_train, y_train)
        y_pred = classifier.predict(X_test)
        f1 = f1_score(y_test, y_pred)
        acc = accuracy_score(y_test, y_pred)

        cx = current_x[best_features]
        real_pred = classifier.predict([cx])
        pred = real_pred[0]
        return dict(
            f1="{:.2f}".format(f1),
            acc="{:.2f}".format(acc),
            pred=int(pred),
            status='buy' if pred == 1 else 'sell'
        )

    async def get_signal(self, profile: dict):
        try:
            insignt = await self.get_insight()
        except Exception as e:
            logging.error(e)
        signal = dict(status='hold', case=None)

        if profile['status'] == 'ready' and insignt['status'] == 'buy':
            signal = dict(status='buy', case="casè1")
        elif profile['status'] == 'bought' and insignt['status'] == 'sell':
            gap = int(time.time()) - int(profile['_ts'])
            if gap > 60 * 60 * 24 * 3:
                signal = dict(status='sell', case="casè2")
            else:
                signal = dict(status='hold', case="casè3")
        else:
            signal = dict(status='hold', case="casè4")
        return signal


async def test():
    algo = AlgoHandler()
    # print(await algo.get_insight())
    print(await algo.get_signal({'status': 'ready', 'id': '1', 'T1': 'bybit'}))

# python -m handlers.algo
if __name__ == "__main__":
    asyncio.run(test())
