# Data Planner

This script generates a plan for recording our labels. It creates several `.csv` files containing the labels to be recorded. In each file, we have labels of the same length; for example, `5.csv` contains labels with a length of 5.



Currently, the following 16 labels are defined in the script:

- `Abi`

- `Sabz`

- `Saal`

- `Ruz`

- `Faramush`

- `Ast`

- `Kheili`

- `Tabestun`

- `Bakht`

- `Diruz`

- `Omidvar`

- `Maman`

- `Baba`

- `Khosh`

- `Like`

- `Dislike`



## Commands

This script includes 6 main commands, which are explained below.

### `generate`

This command creates a new Data Plan.

**Usage:**

Bash

```
python data_planner.py generate <total_data_count> <min_length_of_data> <max_length_of_data> <output_directory> <recorders>
```

- `total_data_count`: The total number of data we want to record.

- `min_length_of_data`: The minimum length of data we want to record.

- `max_length_of_data`: The maximum length of data we want to record.

- `output_directory`: The directory where the plan files will be saved.

- `recorders`: A comma-separated list of recorder names (e.g., `ali,reza,sara`).

### `update`

We use this command if we want to update our data plan.

**Usage:**

Bash

```
python data_planner.py update <total_data_count> <maximum_length_of_data> <data_plan_directory>
```

- `total_data_count`: The new total number of data we want to have.

- `maximum_length_of_data`: The new maximum length of data.

- `data_plan_directory`: The directory where the current data plan is located.

Note that to update, the new total number of data must be greater than the previous one. Also, if you increase the maximum data length, the number of data in previous files might decrease, but the script will not delete them to prevent data loss.

### `count`

This command counts the total number of labels in a specified directory.

**Usage:**

Bash

```
python data_planner.py count <data_directory>
```

- `data_directory`: The directory containing the plan's `.csv` files.

### `upgrade`

This command converts `.csv` files from the old format to the new format. The old format only had `label` and `done` columns, while the new format includes `label`, `total_count`, `done_count`, and dedicated columns for each recorder.

**Usage:**

Bash

```
python data_planner.py upgrade <input_path> <output_path>
```

- `input_path`: The path to the directory containing the old-format `.csv` files.

- `output_path`: The path to the directory where the converted files will be saved.

### `sync`

This command synchronizes the recorded data count (`done_count`) in the `.csv` files based on the existing `.txt` files (which are the actual recorded data).

**Usage:**

Bash

```
python data_planner.py sync <data_path> <csv_path>
```

- `data_path`: The path to the directory where the recorded data (`.txt` files) are located.

- `csv_path`: The path to the directory where the data plan (`.csv`) files are located.

### `stats`

This command calculates and displays statistics on the number of data points recorded by each person.

**Usage:**

Bash

```
python data_planner.py stats <data_dir>
```

- `data_dir`: The path to the directory where the data plan (`.csv`) files are located.