import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load datasets (replace with your actual file paths if needed)
dual_df = pd.read_csv("dual_task_data.csv")
control_df = pd.read_csv("control_grp_data.csv")

# Add a 'Group' column to both for comparison
dual_df["Group"] = "Dual Task"
control_df["Group"] = "Control"

# Combine datasets
combined_df = pd.concat([dual_df, control_df], ignore_index=True)

# ------------------------------
# 1. Histogram for Accuracy
# ------------------------------
plt.figure(figsize=(10, 5))
sns.histplot(data=combined_df, x="accuracy", hue="Group", kde=True, bins=10, palette="Set2", element="step", stat="density")
plt.title("Distribution of Accuracy by Group")
plt.xlabel("Accuracy")
plt.ylabel("Density")
plt.tight_layout()
plt.show()

# ------------------------------
# 2. Histogram for Reaction Time
# ------------------------------
plt.figure(figsize=(10, 5))
sns.histplot(data=combined_df, x="reaction_time", hue="Group", kde=True, bins=10, palette="Set1", element="step", stat="density")
plt.title("Distribution of Reaction Time by Group")
plt.xlabel("Reaction Time (s)")
plt.ylabel("Density")
plt.tight_layout()
plt.show()
