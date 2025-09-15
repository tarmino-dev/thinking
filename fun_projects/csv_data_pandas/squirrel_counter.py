import pandas

# Script which takes data from a CSV file
# and counts how many squirrels with what color of fur are in this file.
# After calculation, the script saves the received data to a new CSV file.

# Read data from csv file
data = pandas.read_csv(
    "2018_Central_Park_Squirrel_Census_-_Squirrel_Data.csv")

# Create new DataFrames for each color using boolean mask (e.g. data["Primary Fur Color"] == "Gray") and count their length
gray_squirrels_count = len(data[data["Primary Fur Color"] == "Gray"])
cinnamon_squirrels_count = len(data[data["Primary Fur Color"] == "Cinnamon"])
black__squirrels_count = len(data[data["Primary Fur Color"] == "Black"])

# Create a dict with the received data
data_dict = {"Fur Color": ["Gray", "Cinnamon", "Black"],
             "Count": [gray_squirrels_count, cinnamon_squirrels_count, black__squirrels_count]}

# Convert the dict to DataFrame
df = pandas.DataFrame(data_dict)

# Save DataFrame as .csv file
df.to_csv("squirrel_count.csv")
