import numpy as np
import random
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

from backtest_meanreversion import run

# ------------------------------------------------------------------------------
# 1) DEFINE / IMPORT YOUR BACKTEST FUNCTION
# ------------------------------------------------------------------------------

def run_backtest(n, top_n, min_rsi, max_rsi, stop_loss, take_profit, num_weeks):
    # profit returns cumulative % profit over past {num_weeks} weeks
    profit = run(num_days_before=n,
                top_n=top_n,
                rsi_low=min_rsi,
                rsi_high=max_rsi,
                stop_loss=stop_loss,
                take_profit=take_profit,
                num_weeks=num_weeks)
    #
    # return profit
    
    # For demonstration, let's just mock a "profit" with some random noise
    # In real code, you'd call your real backtest function
    mock_profit = random.uniform(-10, 10)  # random profit
    return mock_profit

# ------------------------------------------------------------------------------
# 2) GENERATE A DATASET OF (PARAMS -> PROFIT)
# ------------------------------------------------------------------------------
def generate_training_data(num_samples=200):
    """
    Generate training data by sampling parameter combinations 
    and running a backtest to get the resulting profit.
    Return (X, y) arrays.
    """
    X = []
    y = []
    
    for _ in range(num_samples):
        # Sample random parameters in reasonable ranges
        n       = random.randint(5, 30)       # e.g., 5 <= n <= 30
        min_rsi = random.randint(10, 40)      # e.g., 10 <= min_rsi <= 40
        max_rsi = random.randint(50, 90)      # e.g., 50 <= max_rsi <= 90
        sl      = round(random.uniform(0.01, 0.1), 3)  # stop_loss 1% to 10%
        tp      = round(random.uniform(0.02, 0.2), 3)  # take_profit 2% to 20%
        
        profit = run_backtest(n, min_rsi, max_rsi, sl, tp)
        
        # Store inputs (as a 5D vector) and output (profit)
        X.append([n, min_rsi, max_rsi, sl, tp])
        y.append(profit)
    
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)

# ------------------------------------------------------------------------------
# 3) BUILD & TRAIN A SIMPLE NEURAL NETWORK REGRESSOR
# ------------------------------------------------------------------------------
def build_and_train_model(X, y, epochs=50):
    """
    Build a Keras model to learn the mapping: (n, min_rsi, max_rsi, stop_loss, take_profit) -> profit
    """
    model = keras.Sequential([
        layers.Dense(32, activation='relu', input_shape=(5,)),
        layers.Dense(32, activation='relu'),
        layers.Dense(1)  # output = predicted profit
    ])
    
    model.compile(
        optimizer='adam',
        loss='mean_squared_error',
        metrics=['mean_absolute_error']
    )
    
    # Train/validation split
    train_size = int(0.8 * len(X))
    X_train, X_val = X[:train_size], X[train_size:]
    y_train, y_val = y[:train_size], y[train_size:]
    
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=16,
        verbose=1
    )
    
    return model, history

# ------------------------------------------------------------------------------
# 4) SEARCH FOR BEST PARAMETERS USING THE TRAINED MODEL
# ------------------------------------------------------------------------------
def find_best_params_with_model(model, num_search=1000):
    """
    Once the model is trained, we can do a fast "search" over many random parameter sets
    and pick the one that yields the highest predicted profit.
    """
    best_params = None
    best_pred_profit = -999999

    for _ in range(num_search):
        # Sample random parameters in the same range as training
        n       = random.randint(5, 30)
        min_rsi = random.randint(10, 40)
        max_rsi = random.randint(50, 90)
        sl      = round(random.uniform(0.01, 0.1), 3)
        tp      = round(random.uniform(0.02, 0.2), 3)

        x_input = np.array([[n, min_rsi, max_rsi, sl, tp]], dtype=np.float32)
        predicted_profit = model.predict(x_input)[0][0]

        if predicted_profit > best_pred_profit:
            best_pred_profit = predicted_profit
            best_params = (n, min_rsi, max_rsi, sl, tp)

    return best_params, best_pred_profit

# ------------------------------------------------------------------------------
# 5) MAIN EXECUTION LOGIC (Example)
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # Step A: Generate training data by actually running the backtest
    X, y = generate_training_data(num_samples=200)  # Adjust for more or fewer samples

    # Step B: Build and train the model
    model, history = build_and_train_model(X, y, epochs=50)

    # Step C: Use the trained model to search for best parameters
    best_params, best_profit_est = find_best_params_with_model(model, num_search=1000)

    print("---------------------------------------------------")
    print("Best params (based on model prediction):")
    print(f" n={best_params[0]}, min_rsi={best_params[1]}, max_rsi={best_params[2]},"
          f" stop_loss={best_params[3]}, take_profit={best_params[4]}")
    print(f"Predicted Profit = {best_profit_est:.2f}")
    print("---------------------------------------------------")