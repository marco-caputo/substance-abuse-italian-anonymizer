import random
random.seed(42)

def train_test_split(data, train_size=0.8):
    """
    Splits a dataset randomly into train and test/validation subsets.

    :param data: list of samples (any type)
    :param train_size: float in (0,1) or int (number of train samples).
    :return: (train_data, test_data)
    """
    data_copy = list(data)
    random.shuffle(data)
    split_idx = int(len(data_copy) * train_size) if isinstance(train_size, float) else train_size

    train_data = data[:split_idx]
    test_data = data[split_idx:]

    return train_data, test_data