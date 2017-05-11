import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from StockTwits_StockList import ALL_LIST
import csv
import pickle

def load_data_from_file(path):
    """read the file into a list of list, and then a np matrix"""
    stock_file = open(path, "r").read()
    data = np.array(eval(stock_file))
    # print(data.shape)


    date_col = []
    label_col = []
    yesterday_price = 0

    clean_data = list()
    for row in data:
        # change the date to a number
        if list(row).count(0) < 4:
            i = row[0]
            date_num = int("".join(i.split("-")))
            date_col.append(date_num)

            #add label
            today_price = row[6]
            if today_price >= yesterday_price:
                label_col.append(1)
            else:
                label_col.append(-1)
            yesterday_price = today_price
            clean_data.append(row)
    # print(data[0:10,6])
    # print(label_col[0:10])
    #change data to clean data:
    data = np.array(clean_data)

    #delelte the sentiment score and popularity score
    data = data[1:,3:]
    #do not use open and close price
    new_data = np.c_[date_col[1:],data[:,0:3], data[:,5:]]

    # new_data = np.c_[date_col[1:],data]
    # print(new_data.shape)
    # print(new_data[0:3])
    return new_data, label_col[1:]

    # only use the last three column
    # data = data[1:, 11:]
    # return data, label_col[1:]

def apply_naive_bayes(data, label, train_all=False):
    X_train, X_test, y_train, y_test = train_test_split(data, label, test_size = 0.2, random_state = 0)
    train_size = int(len(data)*0.8)
    X_train = data[0:train_size]
    X_test = data[train_size+1:]
    y_train = label[0:train_size]
    y_test = label[train_size+1:]
    # print(train_size)
    # print(X_train.shape)
    # print(X_test.shape)
    clf = GaussianNB()
    if train_all:
        X_train = data
        y_train = label
    clf.fit(X_train, y_train)
    # train_accuracy = clf.score(X_train,y_train)
    accuracy = clf.score(X_test, y_test)
    # print (train_accuracy)
    # print(accuracy)
    probs = clf.predict_proba(X_test)
    print(X_test[0:10])
    print(probs[0:10])
    return accuracy, clf

def apply_neural_network(data,label,train_all=False):
    X_train, X_test, y_train, y_test = train_test_split(data, label, test_size = 0.2, random_state = 0)
    # print(X_train.shape)
    # print(X_test.shape)
    clf = MLPClassifier(solver='adam', alpha=1e-5, hidden_layer_sizes = (5, 5, 2), random_state = 1)
    clf.fit(X_train, y_train)
    train_accuracy = clf.score(X_train,y_train)
    accuracy = clf.score(X_test, y_test)
    # print (train_accuracy)
    # print(accuracy)
    # probs = clf.predict_proba(X_test)
    # print(X_test[0:10])
    # print(probs[0:10])
    return accuracy

def calculate_accuracy_all_stocks(stock_list, ml_algorithm, save_model=False):
    accuracy_dict = dict()
    sample_count = 0
    for stock in stock_list:
        stock_file_path = "./historical_data/" + stock + ".list"
        data, label = load_data_from_file(stock_file_path)
        sample_count += data.shape[0]
        nb_accuracy, model = ml_algorithm(data, label, train_all=True)
        accuracy_dict[stock] = round(nb_accuracy, 2)
        if save_model:
            output_file = "./ml_model/" + stock + ".ml"
            pickle.dump(model, open(output_file, 'wb'))
            print("saved: " + output_file)
    print("total samples from 2015: " + str(sample_count))
    return accuracy_dict

def find_average_accuracy(accuracy_dict):
    accuracies = accuracy_dict.values()
    return sum(accuracies)/float(len(accuracies))

def print_accuracy(accuracy_dict, file_name):
    sorted_accruacy = sorted(accuracy_dict.items(), key=lambda x: x[0], reverse=False)
    out_string = ""
    for k, v in sorted_accruacy:
        out_string += k + ", " + str(v) + "\n"
    average_accuracy = round(find_average_accuracy(accuracy_dict),2)
    out_string += "Average accuracy: " + str(average_accuracy)
    print(out_string)
    with open(file_name, 'wb') as f:
        writer = csv.writer(f)
        writer.writerows(sorted_accruacy)
        writer.writerow(["avg", average_accuracy])





if __name__ == "__main__":
    # accuracy_dict = calculate_accuracy_all_stocks(ALL_LIST, apply_neural_network)
    # print(accuracy_dict)
    # # average_accuracy = find_average_accuracy(accuracy_dict)
    # # print(average_accuracy)
    # print_accuracy(accuracy_dict, "NN_2015_result.csv")

    accuracy_dict = calculate_accuracy_all_stocks(ALL_LIST, apply_naive_bayes, save_model=True)
    print(accuracy_dict)
    average_accuracy = find_average_accuracy(accuracy_dict)
    print(average_accuracy)
    # print_accuracy(accuracy_dict, "NB_2015_result.csv")
    """test a single stock"""
    # stock_file_path = "./historical_data/result/AAPL.list"
    # data, label = load_data_from_file(stock_file_path)
    # print(data.shape)
    # print(len(label))
    # print(data[0:3])
    # print(label[0:3])
    # apply_naive_bayes(data, label)
    # apply_neural_network(data,label)