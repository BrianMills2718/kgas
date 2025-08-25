import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from dowhy import CausalModel
from econml.dml import LinearDML
from sklearn.linear_model import LassoCV
from sklearn.ensemble import RandomForestRegressor

# SET RANDOM SEED FOR REPRODUCIBILITY
np.random.seed(42)

# SYNTHETIC DATA GENERATION
N = 1000  # Number of tweets

# Generate confounders
followers = np.random.lognormal(mean=3, sigma=1, size=N)  # Skewed follower count
time_of_day = np.random.choice([0, 1], size=N)  # Binary (0 = morning, 1 = evening)

# Generate valence (treatment)
valence = np.random.uniform(-1, 1, size=N)  # Sentiment score (-1 to 1)

# Generate retweets (outcome) with causal influence from valence + confounders
retweets = (
    5 + 
    3 * valence + 
    0.05 * followers + 
    2 * time_of_day + 
    np.random.normal(scale=5, size=N)  # Noise term
)

# Create DataFrame
df = pd.DataFrame({
    "valence": valence,
    "retweets": retweets,
    "followers": followers,
    "time_of_day": time_of_day
})

# DISPLAY FIRST 5 ROWS
print(df.head())

# CREATE CAUSAL DAG
G = nx.DiGraph()
G.add_edges_from([
    ("valence", "retweets"),  # Hypothesized causal effect
    ("followers", "retweets"),  # Confounder
    ("time_of_day", "retweets")  # Confounder
])

# PLOT CAUSAL GRAPH
plt.figure(figsize=(5, 3))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=3000, font_size=12)
plt.title("Causal Graph")
plt.show()

# CREATE CAUSAL MODEL WITH DOWHY
model = CausalModel(
    data=df,
    treatment="valence",
    outcome="retweets",
    common_causes=["followers", "time_of_day"]
)

# IDENTIFY EFFECT
identified_estimand = model.identify_effect()
print("Identified Estimand:\n", identified_estimand)

# ESTIMATE CAUSAL EFFECT WITH REGRESSION
estimate = model.estimate_effect(identified_estimand, method_name="backdoor.linear_regression")
print("\nEstimated Causal Effect (Regression):", estimate.value)

# MACHINE LEARNING CAUSAL ESTIMATION WITH ECONML
X = df[["followers", "time_of_day"]]  # Confounders
T = df["valence"]  # Treatment (valence)
Y = df["retweets"]  # Outcome (retweets)

# DOUBLE MACHINE LEARNING MODEL
dml = LinearDML(model_t=LassoCV(), model_y=RandomForestRegressor())
dml.fit(Y, T, X)
treatment_effect = dml.effect(X)

print("\nEstimated Causal Effect (Double ML):", treatment_effect.mean())
