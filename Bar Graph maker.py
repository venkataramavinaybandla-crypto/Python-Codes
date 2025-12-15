import matplotlib.pyplot as plt
import numpy as np

Categories = np.array(["Grains", "Fruit", "Veget-\nables", "Protein", "Dairy", "Sweets"])
values = np.array([689, 891, 908, 741, 496, 231])

choice = input("(Bar Graph / Pie Chart): ")

if choice == "Bar Graph":
    plt.bar(Categories, values, color="green")
    plt.title("Categories")
    plt.xlabel("Consuming Resources")
    plt.ylabel("Value")
    plt.xticks(rotation=0)
    plt.show()

elif choice == "Pie Chart":
    plt.pie(values, labels=Categories, autopct="%1.1f%%")
    plt.title("Categories")
    plt.show()

else:
    print("Invalid choice! Please type Bar Graph or Pie Chart.")
