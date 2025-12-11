import matplotlib.pyplot as plt
import numpy as np

Categories = np.array(["Grains", "Fruit", "Vegetables", "Protein", "Dairy", "Sweets"])
values = np.array([6, 8, 9, 7, 4, 2])

plt.bar(Categories, values, color="skyblue")

plt.title("Categories")
plt.xlabel("Consuming Resources")
plt.ylabel("Value")
plt.xticks(rotation=0)

plt.show()