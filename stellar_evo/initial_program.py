import jax
import jax.numpy as jnp
import jax.lax as lax
import flax.linen as nn
import optax
from flax.training import train_state
import numpy as np
import time

# ─── EVOLVE-BLOCK-START ──────────────────────────────────────────────────────
# ShinkaEvolve will mutate the architecture and logic inside this block.

class StellarNet(nn.Module):
    """The neural network architecture to be evolved."""
    @nn.compact
    def __call__(self, x):
        # Current baseline: Two layers of 128 units
        x = nn.Dense(128)(x)
        x = nn.relu(x)
        x = nn.Dense(128)(x)
        x = nn.relu(x)
        # Output 4 values: Teff, L, delta_nu, nu_max
        x = nn.Dense(4)(x) 
        return x

def get_training_config():
    """Returns hyperparameters that Shinka can also mutate."""
    return {
        "learning_rate": 0.001,
        "batch_size": 4096,
        "epochs": 500,
        "optimizer": "adam" # Shinka might change this to 'adamw' or add weight decay
    }

# ─── EVOLVE-BLOCK-END ────────────────────────────────────────────────────────


# ─── Fixed interface (not evolved) ───────────────────────────────────────────

def unstandardize(data, stats, feature_names):
    import numpy as np
    unstd_data = np.array(data)
    for i, name in enumerate(feature_names):
        mean = stats[name]['mean']
        std = stats[name]['std']
        unstd_data[:, i] = (data[:, i] * std) + mean
    return unstd_data

def run_training(train_data, val_data, test_data, features, targets, feature_stats, target_stats):
    """
    Main entrypoint called by evaluate.py.
    This uses your 'ultra-optimized' JAX logic.
    """
    config = get_training_config()
    
    # Unpack Data
    X_train_raw, y_train_raw = train_data
    X_val, y_val = val_data
    X_test_raw, y_test_raw = test_data
    
    batch_size = config["batch_size"]
    epochs = config["epochs"]
    
    num_samples = X_train_raw.shape[0]
    n_batches = num_samples // batch_size
    
    # Truncate for static XLA shapes
    X_train = X_train_raw[:n_batches * batch_size]
    y_train = y_train_raw[:n_batches * batch_size]

    # 1. Initialize Model & State
    model = StellarNet()
    key = jax.random.PRNGKey(0)
    variables = model.init(key, jnp.ones((1, len(features))))
    
    tx = optax.adam(learning_rate=config["learning_rate"])
    state = train_state.TrainState.create(
        apply_fn=model.apply, 
        params=variables['params'], 
        tx=tx
    )

    # 2. Optimized Inner Batch Loop (lax.scan)
    def batch_step(carry_state, batch):
        x, y = batch
        def loss_fn(p):
            pred = carry_state.apply_fn({'params': p}, x)
            return jnp.mean((pred - y) ** 2)
        loss, grads = jax.value_and_grad(loss_fn)(carry_state.params)
        new_state = carry_state.apply_gradients(grads=grads)
        return new_state, loss

    @jax.jit
    def run_full_epoch(current_state, x_data, y_data):
        x_batched = x_data.reshape(n_batches, batch_size, -1)
        y_batched = y_data.reshape(n_batches, batch_size, -1)
        final_state, batch_losses = lax.scan(batch_step, current_state, (x_batched, y_batched))
        return final_state, jnp.mean(batch_losses)

    @jax.jit
    def get_val_loss(params, x, y):
        return jnp.mean((model.apply({'params': params}, x) - y) ** 2)

    # 3. Training Loop
    for epoch in range(1, epochs + 1):
        key, subkey = jax.random.split(key)
        perms = jax.random.permutation(subkey, n_batches * batch_size)
        state, _ = run_full_epoch(state, X_train[perms], y_train[perms])

    # 4. Final Evaluation for Fitness
    
    X_test = jnp.array(test_data[0], dtype=jnp.float32)
    y_test = jnp.array(test_data[1], dtype=jnp.float32)
    
    predictions = state.apply_fn({'params': state.params}, X_test)
    
    # Unstandardize predictions and y_test
    predictions_unstd = unstandardize(predictions, target_stats, targets)
    y_test_unstd = unstandardize(y_test, target_stats, targets)
    
    test_residuals = y_test_unstd - predictions_unstd
    
    val_predictions = state.apply_fn({'params': state.params}, X_val)
    val_predictions_unstd = unstandardize(val_predictions, target_stats, targets)
    y_val_unstd = unstandardize(y_val, target_stats, targets)
    val_loss = jnp.mean((val_predictions_unstd - y_val_unstd) ** 2)
    
    return {
        "val_loss": float(val_loss),
        "test_residuals": test_residuals,
        "y_test": y_test_unstd,
        "params": state.params,
        "model": model
    }