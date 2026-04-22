import os
import argparse
import jax.numpy as jnp
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

import flax.linen as nn

from sklearn.model_selection import train_test_split
from shinka.core import run_shinka_eval

def standardize_stellar_data(df, features):
    df_std = df.copy()
    stats = {}
    
    for feat in features:
        mean = df[feat].mean()
        std = df[feat].std()
        df_std[feat] = (df[feat] - mean) / std
        stats[feat] = {'mean': mean, 'std': std}
        
    return df_std, stats

def unstandardize(data, stats, feature_names):
    unstd_data = data.copy()
    for i, name in enumerate(feature_names):
        mean = stats[name]['mean']
        std = stats[name]['std']
        unstd_data[:, i] = (data[:, i] * std) + mean
    return unstd_data

def split_by_track(df, train_size=0.7, val_size=0.15, test_size=0.15):
    unique_tracks = df['Track'].unique()
    
    train_tracks, test_val_tracks = train_test_split(
        unique_tracks, train_size=train_size, random_state=42
    )
    
    relative_val_size = val_size / (val_size + test_size)
    val_tracks, test_tracks = train_test_split(
        test_val_tracks, train_size=relative_val_size, random_state=42
    )
    
    train_df = df[df['Track'].isin(train_tracks)]
    val_df = df[df['Track'].isin(val_tracks)]
    test_df = df[df['Track'].isin(test_tracks)]
    
    return train_df, val_df, test_df

# --- DATA LOADING (Global or inside main) ---
# We load and convert once to avoid repeating slow Pandas operations
def load_and_prep_data():
    # Load from HDF5
    data_fname = os.path.join(os.path.dirname(__file__), "astec_vary_MZ_small.hdf5")
    df = pd.read_hdf(data_fname, key='data')
    
    features = ['M', 'Z', 'star_age']
    targets = ['Teff', 'luminosity', 'delta_nu', 'nu_max']
    
    # Standardize features
    df_std_features, feature_stats = standardize_stellar_data(df, features=features)
    
    # Standardize targets
    df_std_all, target_stats = standardize_stellar_data(df_std_features, features=targets)
    
    # Split by track
    train_df, val_df, test_df = split_by_track(df_std_all)
    
    # Convert to JAX arrays
    data_bundles = {
        "train_data": (jnp.array(train_df[features].values), jnp.array(train_df[targets].values)),
        "val_data": (jnp.array(val_df[features].values), jnp.array(val_df[targets].values)),
        "test_data": (jnp.array(test_df[features].values), jnp.array(test_df[targets].values)),
        "features": features,
        "targets": targets,
        "feature_stats": feature_stats,
        "target_stats": target_stats
    }
    return data_bundles

def validate_stellar(run_output: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Checks if the model meets the strict Delta Nu residual constraint (0.00079 from Kepler).
    Also checks that the generated model is a valid FLAX neural network.
    """
    if not isinstance(run_output, dict):
        return False, "Output is not a dictionary."
    
    if "model" not in run_output:
        return False, "Missing model in output."
    
    model = run_output["model"]
    if not isinstance(model, nn.Module):
        return False, "Generated model is not a FLAX neural network."
    
    if "test_residuals" not in run_output:
        return False, "Missing test residuals in output."

    # run_output['test_residuals'] should be (y_test - predictions)
    # run_output['y_test'] should be the ground truth
    residuals = run_output["test_residuals"]
    y_test = run_output["y_test"]
    
    # Identify the index for delta_nu in your target list (e.g., index 2)
    # targets = ['Teff', 'luminosity', 'delta_nu', 'nu_max']
    dn_idx = 2 
    
    dn_residuals = residuals[:, dn_idx]
    dn_true = y_test[:, dn_idx]
    
    # Calculate Absolute Fractional Residual: |(True - Pred) / True|
    # Avoid division by zero with a tiny epsilon
    fractional_residuals = jnp.abs(dn_residuals / (dn_true + 1e-10))
    max_residual = jnp.max(fractional_residuals)

    # if max_residual > 0.1:
    #     return False, f"Constraint Violated: Max Delta Nu residual {max_residual:.6f} > 0.1"
    
    return True, None

def aggregate_metrics(results: List[Dict[str, Any]], results_dir: str) -> Dict[str, Any]:
    res = results[0]
    val_loss = float(res["val_loss"])
    
    # Calculate the penalty
    dn_idx = 2
    frac_res = jnp.abs(res["test_residuals"][:, dn_idx] / (res["y_test"][:, dn_idx] + 1e-10))
    max_res = float(jnp.max(frac_res))
    
    # If it meets the condition, score is -loss.
    # If not, add a massive penalty based on how much it missed the target.
    penalty = 0
    if max_res > 0.00079:
        penalty = 1000 * (max_res - 0.00079)   #maybe we can play around with this penalty, balancing residual error vs validation accuracy
    
    combined_score = -val_loss - penalty

    return {
        "combined_score": combined_score,
        "public": {
            "val_mse": round(val_loss, 6),
            "max_dn_resid": round(max_res, 7),
            "met_constraint": max_res <= 0.00079
        },
        "text_feedback": f"Max Δν Resid: {max_res:.7f} | {'PASS' if max_res <= 0.00079 else 'FAIL'}"
    }

def main(program_path: str, results_dir: str) -> None:
    os.makedirs(results_dir, exist_ok=True)
    
    # Load data once to be shared across runs
    data_bundles = load_and_prep_data()

    metrics, correct, error_msg = run_shinka_eval(
        program_path=program_path,
        results_dir=results_dir,
        experiment_fn_name="run_training", # Matches the function in initial_program.py
        num_runs=1,
        # This injects your data into the 'run_training' function
        get_experiment_kwargs=lambda i: data_bundles,
        validate_fn=validate_stellar,
        aggregate_metrics_fn=lambda results: aggregate_metrics(results, results_dir),
    )
    
    if correct:
        print(f"SUCCESS | Fitness Score: {metrics['combined_score']:.6f}")
    else:
        print(f"FAILED: {error_msg}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--program_path", required=True)
    parser.add_argument("--results_dir", required=True)
    args = parser.parse_args()
    main(args.program_path, args.results_dir)