import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the datasets
dual_df = pd.read_csv("dual_task_data.csv")
control_df = pd.read_csv("control_grp_data.csv")

# ------------------------------
# 1. Overall averages
# ------------------------------
dual_accuracy = dual_df["accuracy"].mean()
dual_rt = dual_df["reaction_time"].mean()

control_accuracy = control_df["accuracy"].mean()
control_rt = control_df["reaction_time"].mean()

print(f"Dual Task - Average Accuracy: {dual_accuracy:.3f}")
print(f"Dual Task - Average Reaction Time: {dual_rt:.3f}")
print(f"Control Task - Average Accuracy: {control_accuracy:.3f}")
print(f"Control Task - Average Reaction Time: {control_rt:.3f}")

# ------------------------------
# 2. Combine data for comparison
# ------------------------------
comparison_df = pd.DataFrame({
    "Task Type": ["Dual Task", "Control Task"],
    "Accuracy": [dual_accuracy, control_accuracy],
    "Reaction Time": [dual_rt, control_rt]
})

# ------------------------------
# 3. Averages by gender
# ------------------------------
# Add a "Task Type" column to distinguish between datasets
dual_df["Task Type"] = "Dual Task"
control_df["Task Type"] = "Control Task"

# Combine both datasets
combined_df = pd.concat([dual_df, control_df])

# Group by gender and task type
gender_stats = combined_df.groupby(["gender", "Task Type"])[["accuracy", "reaction_time"]].mean().reset_index()
print("\nAverages by Gender and Task Type:")
print(gender_stats)

# ------------------------------
# 4. Plotting
# ------------------------------
sns.set(style="whitegrid")

# Plot overall averages comparison
fig, axs = plt.subplots(2, 2, figsize=(14, 10))

# Accuracy comparison
sns.barplot(data=comparison_df, x="Task Type", y="Accuracy", ax=axs[0, 0], palette="Blues_d")
axs[0, 0].set_title("Average Accuracy Comparison")
axs[0, 0].set_ylim(0, 1)
axs[0, 0].set_ylabel("Accuracy")

# Reaction time comparison
sns.barplot(data=comparison_df, x="Task Type", y="Reaction Time", ax=axs[0, 1], palette="Reds_d")
axs[0, 1].set_title("Average Reaction Time Comparison")
axs[0, 1].set_ylabel("Reaction Time (ms)")

# Accuracy by gender and task type
sns.barplot(data=gender_stats, x="gender", y="accuracy", hue="Task Type", ax=axs[1, 0], palette="Blues_d")
axs[1, 0].set_title("Accuracy by Gender and Task Type")
axs[1, 0].set_ylim(0, 1)
axs[1, 0].set_ylabel("Accuracy")

# Reaction time by gender and task type
sns.barplot(data=gender_stats, x="gender", y="reaction_time", hue="Task Type", ax=axs[1, 1], palette="Reds_d")
axs[1, 1].set_title("Reaction Time by Gender and Task Type")
axs[1, 1].set_ylabel("Reaction Time (ms)")

plt.tight_layout()
plt.show()