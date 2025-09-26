import numpy as np
import pandas as pd
import sys
from typing import List
import os
import re 
import random

INDEX2LABEL = {
    0: "Abi",
    1: "Sabz",
    2: "Saal",
    3: "Ruz",
    4: "Faramush",
    5: "Ast",
    6: "Kheili",
    7: "Tabestun",
    8: "Bakht",
    9: "Diruz",
    10: "Omidvar",
    11: "Maman",
    12: "Baba",
    13: "Khosh",
    14: "Like",
    15: "Dislike"
}

def sign(x):
    if x > 0:
        return 1
    if x == 0:
        return 0
    
def nlog2n(length: int) -> float:
    '''
    Calculates n * log2(n). It is needed to know how many data to generate for each data length.
    :param length: length of data
    :return: length * log2(length)
    '''
    return length * np.log2(length + 1)

def fill_count_array(n: int, min_length: int, max_length: int) -> List[int]:
    '''
    Fills an array with the number of data to generate for each data length.
    :param n: number of data to generate
    :pararm min_length: minimum length of data
    :pararm max_length: maximum length of data
    :return List[int]: array with the number of data to generate for each data length
    '''
    # caluclate nlog2(n) for each data length and scale them to the number of data to generate
    # arr = [nlog2n(i) for i in range(1, max_length + 1)]x
    # scale = sum(arr) / n
    arr = [n // (max_length - min_length + 1) for _ in range(min_length, max_length + 1)]
    # if the sum of the array is less than n, add 1 by 1 to the array until the sum is equal to n
    remainder = n - sum(arr)
    for i in range(remainder):
        arr[i] += 1
    return arr

def generate_label(length: int) -> str:
    '''
    Generates a random data with the given length.
    :param length: length of data
    :return str: The generated data
    '''
    label = list(np.random.randint(0, len(INDEX2LABEL.keys()), length))
    label = [INDEX2LABEL[index] for index in label]
    return ''.join(label)

def generate_df(length: int, count: int, recorders: List[str]) -> None:
    '''
    Generates a blank csv file containing data with the given length.
    :param length: length of data
    :param count: number of data to generate;
    :param recorders: A list containing the names of recorders
    '''
    labels = []
    # set random seed to generate reproducible data
    np.random.seed(98)
    # init dictionaries
    df_dict = {"label": [], "done_count": [], "total_count": []}
    label_check_dict = {}
    # generate labels for length l    
    for _ in range(count):
        label = generate_label(length)
        # if the label is new, create a new row in df
        if label not in label_check_dict:
            df_dict['label'].append(label)
            df_dict['done_count'].append(0)
            df_dict['total_count'].append(1)
            label_check_dict[label] = len(df_dict['label']) - 1
        else:
            # if the label is not new, increment its total_count
            df_dict['total_count'][label_check_dict[label]] = df_dict['total_count'][label_check_dict[label]] + 1
    # fill done_count and total_count for each recorder
    for name in recorders:
        df_dict[f'{name}_done_count'] = []
        df_dict[f'{name}_total_count'] = []
    
    for total_count in df_dict['total_count']:
        each_count = total_count // len(recorders)
        remaining = total_count - each_count * len(recorders)
        shuffled_recorders = random.sample(recorders, len(recorders))
        for name in recorders:
            df_dict[f'{name}_done_count'].append(0)
            df_dict[f'{name}_total_count'].append(each_count + (shuffled_recorders.index(name) < remaining))

    # create the dataframe
    df = pd.DataFrame(df_dict)
    return df

def generate_data(n: int, min_length: int, max_length: int, dir_path: str, recorders: List[str]) -> None:
    '''
    Generates a csv file for each data length containing the data to record.
    :param n: number of data to generate
    :param min_length: minimum length of data
    :param max_length: maximum length of data
    :param dir_path: directory path to save the csv files
    :param recorders: A list containing the names of recorders
    '''
    # fill an array with the number of data to generate for each data length
    counts = fill_count_array(n, min_length, max_length)
    # generate data for each data length
    print(counts)
    for l in range(min_length, max_length + 1):
        df = generate_df(l, counts[l - min_length], recorders)
        df.to_csv(f'{dir_path}/{l}.csv')

def update_data(n: int, max_length: int, dir_path: str) -> List[int]:
    '''
    Updates the csv files in the given directory.
    :param n: number of data to generate
    :param max_length: maximum length of data
    :param dir_path: directory path to save the csv files
    :return List[int]: a list of skipped data lengths because the new count is less than the old count
    '''
    # fill an array with the number of data to generate for each data length
    counts = fill_count_array(n, max_length)
    skipped_lengths = []
    # generate data for each data length
    for l in range(1, max_length + 1):
        # if csv file does not exist, generate the file
        if not os.path.exists(f'{dir_path}/{l}.csv'):
            # create new dataframe
            df = generate_df(l, counts[l - 1])
            # save dataframe
            df.to_csv(f'{dir_path}/{l}.csv', index=False)
        # if csv file exists, update the file
        else:
            info = get_file_info(f'{dir_path}/{l}.csv')
            # if the number of data to generate is less than the number of already done data, skip
            if counts[l - 1] <= info['count']:
                skipped_lengths.append(l)
            else:
                # create new dataframe
                df = generate_df(l, counts[l - 1])
                # update done data
                for i in range(info['done']):
                    df.at[i, 'done'] = 1
                # save dataframe
                df.to_csv(f'{dir_path}/{l}.csv', index=False)
    return skipped_lengths

def exist_csv(dir_path: str) -> bool:
    '''
    Checks if there are csv files in the given directory.
    :param dir_path: directory path to check
    :return bool: True if there are csv files in the directory, False otherwise
    '''
    file_names = os.listdir(dir_path)
    for name in file_names:
        if name.endswith(".csv") and name.split('.')[0].isdigit():
            return True
    return False

def count_data(dir_path: str) -> int:
    '''
    Counts the number of data in the given directory.
    :param dir_path: directory path to check
    :return int: number of data
    '''
    count = 0
    file_names = os.listdir(dir_path)
    for name in file_names:
        if name.endswith(".csv") and name.split('.')[0].isdigit():
            df = pd.read_csv(f'{dir_path}/{name}')
            count += len(df)
    return count
    
def get_file_info(file_path: str) -> dict:
    '''
    Counts the number of data and done data in csv file.
    :param file_path: csv file path to check
    :return int: number of done data
    '''
    df = pd.read_csv(file_path)
    return {
        "count": len(df),
        "done": sum(df["done"])
    }

def shit2sheet(input_path: str, output_path: str):
    '''
    Takes a path containing generated csv files (with legAcy format) and converts them to the new format.
    The new format consists of 3 columns (label, total_count, done_count)
    :param input_path str: The path to the root folder of generated csv files. 
    :param output_path: The path to create the new files
    '''
    csv_files = [file for file in os.listdir(input_path) if file.endswith('csv')]
    failed_files = []
    for csv_file in csv_files:
        df = pd.read_csv(f'{input_path}/{csv_file}')
        # Check if the files is in legacy format
        if set(df.columns) != {'label', 'done'}:
            failed_files.append(csv_file)
            continue;
        # Add label counts and done counts and remove previous "done" column
        counts = df['label'].value_counts()
        new_df = {'label': [], 'total_count': [], 'done_count': []}
        check_dict = dict()
        for label in df['label'].values:
            if not label in check_dict:
                total_count = counts[label]
                done_count = df[df['label'] == label]['done'].sum()
                # new_row = np.array([label, total_count, done_count])
                new_df['label'].append(label)
                new_df['total_count'].append(total_count)
                new_df['done_count'].append(done_count)
                check_dict[label] = 1
        new_df = pd.DataFrame(new_df)
        print(new_df)
        print(new_df['total_count'].sum())
        # Create output dir
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        # Save the file
        new_df.to_csv(f'{output_path}/{csv_file}')

def sync(data_path: str, csv_path: str):
    data_files = [f'{data_path}/{file}' for file in os.listdir(data_path) if file.endswith('.txt')]
    dic = dict()
    # get info based on data length
    for file_name in data_files:
        label = file_name.split("/")[-1].split(".")[0] if "/" in file_name else file_name.split(".")[0]
        moves = re.findall('[A-Z][^A-Z]*', label)
        with open(file_name, 'r') as fp:
            num_data = fp.read().count(';')
            if len(moves) not in dic:
                dic[len(moves)] = []
            dic[len(moves)].append((label, num_data))
    # update csv files
    i = 1
    while i > 0:
        if i not in dic:
            break
        df = pd.read_csv(f'{csv_path}/{i}.csv', index_col=0)
        count = 0
        for data in dic[i]:
            index = int(df.index[df['label'] == data[0]][0])
            count += data[1]
            # print(data[0], index)
            df.loc[index, 'done_count'] = data[1]

        df.to_csv(f'{csv_path}/{i}.csv')
        i += 1

def get_stats(data_dir: str):
    csv_files = [f'{data_dir}/{file}' for file in os.listdir(data_dir) if file.endswith('.csv')]
    if len(csv_files) == 0:
        raise ValueError('The path does not contain any csv file!')
    recorders_data_count = {name:0 for name in pd.read_csv(csv_files[0]).columns if name.endswith('done_count')}
    recorders_data_count.pop('done_count')
    for file in csv_files:
        df = pd.read_csv(file)
        for name in recorders_data_count:
            recorders_data_count[name] += df[name].sum()
    recorders_data_count['total_done_count'] = sum(recorders_data_count.values())
    return recorders_data_count
                            
    
        
if __name__ == '__main__':
    # get the command
    args = sys.argv
    command = args[1]

    if command == 'generate':
        n = int(args[2])
        min_length = int(args[3])
        max_length = int(args[4])
        dir_path = args[5]
        recorders = args[6].split(',')
        
        # check if directory exists (if not, create it)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # check if there are csv files in the directory
        elif exist_csv(dir_path):
            print('There are already csv files in the directory. Are you sure to continue? (y/n)')
            answer = input()
            if answer == 'n':
                print('Canceled.')
                exit()

        generate_data(n, min_length, max_length, dir_path, recorders)
        print('Done.')

    elif command == 'count':
        dir_path = args[2]
        if not os.path.exists(dir_path):
            print('The directory does not exist.')
        else:
            print('Total number of data:', count_data(dir_path))

    elif command == 'update':
        n = int(args[2])
        max_length = int(args[3])
        dir_path = args[4]
        skipped_lengths = update_data(n, max_length, dir_path)
        if len(skipped_lengths) > 0:
            print('Skipped data lengths:', skipped_lengths)
        print('Done.')

    elif command == 'upgrade':
        input_path, output_path = args[2], args[3]
        shit2sheet(input_path, output_path)

    elif command == 'sync':
        data_path, csv_path = args[2], args[3]
        sync(data_path, csv_path)

    elif command == "stats":
        data_dir = args[2]
        print(get_stats(data_dir))

    else:
        raise Exception("You've entered a wrong command!")