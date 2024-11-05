from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import f1_score, accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from ta import add_all_ta_features

import pandas as pd
import ccxt.async_support as ccxt
import logging
import asyncio


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

    async def get_nomalized_data(self, symbol, timeframe):
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
        return dict(
            df=_all_data,
            X_new=X_new,
            y=y,
            current_x=current_x,
            best_features=best_features
        )

    async def get_up_down_score(self, data, rate):
        new_y = []
        df = data['df']
        for close, target in zip(df['close'], data['y']):
            if target > close * rate:
                new_y.append(1)
            else:
                new_y.append(0)

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
        X_train, X_test, y_train, y_test = train_test_split(
            data['X_new'], new_y, test_size=0.2, random_state=42)

        classifier.fit(X_train, y_train)
        y_pred = classifier.predict(X_test)
        f1 = f1_score(y_test, y_pred)
        acc = accuracy_score(y_test, y_pred)

        cx = data['current_x'][data['best_features']]
        real_pred = classifier.predict([cx])
        pred = real_pred[0]

        if rate > 1 and pred == 1 and f1 > 0.75:
            status = 'up'
        elif rate < 1 and pred == 1 and f1 > 0.75:
            status = 'down'
        else:
            status = 'hold'

        return dict(
            f1="{:.2f}".format(f1),
            acc="{:.2f}".format(acc),
            pred=int(pred),
            status=status
        )

    async def get_insight(self):
        data = await self.get_nomalized_data('ETH/USDT', '1d')

        up_score = await self.get_up_down_score(data, 1.02)
        down_score = await self.get_up_down_score(data, 0.98)

        if up_score['status'] == 'up' and down_score['status'] == 'down':
            if up_score['f1'] > down_score['f1']:
                status = 'up'
            else:
                status = 'down'
        elif up_score['status'] == 'up':
            status = 'up'
        elif down_score['status'] == 'down':
            status = 'down'
        else:
            status = 'hold'
        return dict(
            up_score=up_score,
            down_score=down_score,
            status=status
        )

    async def get_signal(self, profile: dict):
        try:
            insignt = await self.get_insight()
            print(insignt)
        except Exception as e:
            logging.error(e)
        signal = dict(status='hold', case=None)

        if profile['status'] == 'ready' and insignt['status'] == 'up':
            signal = dict(actions=['buy'], items=['ETH3LUSDT'], case="case1")
        elif profile['status'] == 'bought3L' and insignt['status'] == 'down':
            signal = dict(
                actions=['sell', 'buy'],
                items=['ETH3LUSDT', 'ETH3SUSDT'],
                case="case2")
        elif profile['status'] == 'bought3L' and insignt['status'] == 'up':
            signal = dict(actions=['hold'], items=['ETH3LUSDT'], case="case3")
        elif profile['status'] == 'bought3L' and insignt['status'] == 'hold':
            signal = dict(actions=['sell'], items=['ETH3SUSDT'], case="case4")
        elif profile['status'] == 'ready' and insignt['status'] == 'down':
            signal = dict(actions=['buy'], items=['ETH3SUSDT'], case="case5")
        elif profile['status'] == 'bought3S' and insignt['status'] == 'down':
            signal = dict(actions=['hold'], items=['ETH3SUSDT'], case="case6")
        elif profile['status'] == 'bought3S' and insignt['status'] == 'up':
            signal = dict(
                actions=['sell', 'buy'],
                items=['ETH3SUSDT', 'ETH3LUSDT'],
                case="case7")
        elif profile['status'] == 'bought3S' and insignt['status'] == 'hold':
            signal = dict(actions=['sell'], items=['ETH3SUSDT'], case="case8")
        else:
            signal = dict(status='hold', case="case10")
        return signal


async def test():
    algo = AlgoHandler()
    # print(await algo.get_insight())
    print(await algo.get_signal({'status': 'ready', 'id': '1', 'T1': 'bybit'}))

# python -m handlers.algo
if __name__ == "__main__":
    asyncio.run(test())
