from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import f1_score, accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from ta import add_all_ta_features

import pandas as pd
import numpy as np
import ccxt.async_support as ccxt
import logging
import asyncio
import random


class AlgoHandler():
    def run(self):
        logging.info("Hello from AlgoHandler")

    async def get_data(self, symbol, timeframe):
        bybit = ccxt.bybit()

        async with bybit:
            # etc_ohlcv = await bybit.fetch_ohlcv('ETH/USDT', '1d')
            # max data
            etc_ohlcv = await bybit.fetch_ohlcv(symbol, timeframe, limit=400)
            df = pd.DataFrame(
                etc_ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['Datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df

    async def get_nomalized_data(self, symbol, timeframe, shift=5):
        # df = await self.get_data('ETH/USDT', '1d')
        try:
            df = await self.get_data(symbol, timeframe)
        except Exception as e:
            logging.error(e)
            return None
        df = df[['Datetime', 'open', 'high', 'low', 'close', 'volume']]
        df.set_index('Datetime', inplace=True)
        _all_data = add_all_ta_features(
            df,
            open="open", high="high", low="low", close="close", volume="volume"
        )

        _all_data = _all_data.drop(
            ['trend_psar_down', 'trend_psar_up'], axis=1)
        _all_data.dropna(inplace=True)
        _all_data['target'] = _all_data['close'].shift(-shift)
        current_x = _all_data.iloc[-1].drop('target')
        _all_data.dropna(inplace=True)

        X = _all_data.drop('target', axis=1)
        y = _all_data['target']

        k_best = SelectKBest(f_classif, k=20)
        k_best.fit(X, y)
        X.columns[k_best.get_support()]

        best_features = X.columns[k_best.get_support()]

        X_new = X[best_features]
        return dict(
            df=_all_data,
            X_new=X_new,
            y=y,
            current_x=current_x,
            best_features=best_features
        )

    async def get_up_down_score(self, data):
        new_y = []
        df = data['df']
        # y = np.where(X['Close'].shift(-5) > X['Close'], 1, -1)
        new_y = np.where(df['close'].shift(-5) > df['close'], 1, -1)

        # GridSearchCV - RandomForestClassifier
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, 15, 20],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }

        classifier = RandomForestClassifier()
        grid_search = GridSearchCV(
            classifier, param_grid, cv=5, n_jobs=-1, verbose=2)
        grid_search.fit(data['X_new'], new_y)
        print(grid_search.best_params_)

        classifier = RandomForestClassifier(
            max_depth=grid_search.best_params_['max_depth'],
            min_samples_leaf=grid_search.best_params_['min_samples_leaf'],
            min_samples_split=grid_search.best_params_['min_samples_split'],
            n_estimators=grid_search.best_params_['n_estimators']
        )

        # val = cross_val_score(classifier, data['X_new'], new_y, cv=5)
        # print(val)
        repect = 10
        preds, f1s, accs = [], [], []
        for x in range(1, repect):
            X_train, X_test, y_train, y_test = train_test_split(
                data['X_new'],
                new_y,
                test_size=0.2,
                random_state=random.randint(1, 100))

            classifier.fit(X_train, y_train)
            y_pred = classifier.predict(X_test)
            f1 = f1_score(y_test, y_pred)
            acc = accuracy_score(y_test, y_pred)

            f1s.append(f1)
            accs.append(acc)

            cx = data['current_x'][data['best_features']]
            real_pred = classifier.predict([cx])
            pred = real_pred[0]
            preds.append(pred)

        f1 = sum(f1s) / repect
        acc = sum(accs) / repect
        pred = sum(preds) / repect

        # if rate > 1 and pred == 1 and f1 > 0.75:
        print(pred)
        # if rate > 1 and pred > 0.7 and (f1+acc) > 1.4:
        if pred > 0:
            status = 'up'
        elif pred <= 0:
            status = 'down'
        else:
            status = 'hold'

        return dict(
            f1="{:.2f}".format(f1),
            acc="{:.2f}".format(acc),
            pred="{:.2f}".format(pred),
            status=status
        )

    async def get_insight(self):
        symbol = 'BTC/USDT'
        interval = '1d'
        # up_score_rate = 1.01
        # down_score_rate = 0.99

        data = await self.get_nomalized_data(symbol, interval, shift=5)
        # up_score = await self.get_up_down_score(data, up_score_rate)
        # down_score = await self.get_up_down_score(data, down_score_rate)
        score = await self.get_up_down_score(data)
        # print(score)
        # if up_score['status'] == 'up' and down_score['status'] == 'down':
        #     if up_score['f1'] > down_score['f1']:
        #         status = 'up'
        #     else:
        #         status = 'down'
        # elif up_score['status'] == 'up':
        #     status = 'up'
        # elif down_score['status'] == 'down':
        #     status = 'down'
        # else:
        #     status = 'hold'
        # return dict(
        #     up_score=up_score,
        #     down_score=down_score,
        #     status=status
        # )
        return score

    async def get_signal(self, profile: dict):
        try:
            insignt = await self.get_insight()
            print(insignt)
        except Exception as e:
            logging.error(e)
        signal = dict(status='hold', case=None)
        target = "BTC"

        if profile['status'] == 'ready' and insignt['status'] == 'up':
            signal = dict(
                actions=['buy'],
                items=[f'{target}3LUSDT'],
                case="case1")
        elif profile['status'] == 'bought3L' and insignt['status'] == 'down':
            signal = dict(
                actions=['sell', 'buy'],
                items=[f'{target}3LUSDT', f'{target}3SUSDT'],
                case="case2")
        elif profile['status'] == 'bought3L' and insignt['status'] == 'up':
            signal = dict(
                actions=['hold'],
                items=[f'{target}3LUSDT'],
                case="case3")
        elif profile['status'] == 'bought3L' and insignt['status'] == 'hold':
            signal = dict(
                actions=['sell'],
                items=[f'{target}3LUSDT'],
                case="case4")
        elif profile['status'] == 'ready' and insignt['status'] == 'down':
            signal = dict(
                actions=['buy'],
                items=[f'{target}3SUSDT'],
                case="case5")
        elif profile['status'] == 'bought3S' and insignt['status'] == 'down':
            signal = dict(
                actions=['hold'],
                items=[f'{target}3SUSDT'],
                case="case6")
        elif profile['status'] == 'bought3S' and insignt['status'] == 'up':
            signal = dict(
                actions=['sell', 'buy'],
                items=[f'{target}3SUSDT', f'{target}3LUSDT'],
                case="case7")
        elif profile['status'] == 'bought3S' and insignt['status'] == 'hold':
            signal = dict(
                actions=['sell'],
                items=[f'{target}3SUSDT'],
                case="case8")
        else:
            signal = dict(
                actions=['hold'],
                items=['ELSE'],
                case="case10")
        return signal


async def test():
    algo = AlgoHandler()
    print(await algo.get_insight())
    # print(await algo.get_signal({'status': 'ready', 'id': '1', 'T1': 'bybit'}))
    # print(await algo.get_data('ETH/USDT', '4h'))

# python -m handlers.core.algo
if __name__ == "__main__":
    asyncio.run(test())
