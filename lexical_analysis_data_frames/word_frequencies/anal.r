install.packages(c("ragg", "reprex"))


install.packages("tidyverse")

# Load necessary library
library(readr)

# Define the file path
file_path <- "word_counts_all.csv"  # Replace with your actual file path

# Load the CSV file
df <- read_csv(file_path)

# Load necessary libraries
library(tidyverse)
library(yarrr)

# Reshape data from wide to long
df_long <- df %>%
  gather(key = "participant", value = "frequency", -word, -category) %>%
  mutate(participant = as.numeric(participant))  # Ensure participant is numeric

# Create groups based on participant number
df_long <- df_long %>%
  mutate(group = cut(participant, breaks = seq(0, max(participant) + 100, by = 100),
                     labels = seq(100, max(participant), by = 100), 
                     include.lowest = TRUE))

# Filter data for the word "the"
df_filtered <- df_long %>%
  filter(word == "the")

# Create the pirateplot
pirateplot(frequency ~ group, data = df_filtered,
           main = "Pirate plot example",
           pal = "southpark",
           theme = 3)
