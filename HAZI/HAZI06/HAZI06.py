import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn import datasets
class Node():
    def __init__(self, feature_index=None, threshold=None, left=None, right=None, info_gain=None, value=None) -> None:
        self.feature_index=feature_index
        self.threshold=threshold
        self.left=left
        self.right=right
        self.info_gain=info_gain
        self.value=value

class DecisionTreeClassifier():
    def __init__(self, min_samples_split=2, max_depth=2):
        
        self.root = None
        
        self.min_samples_split = min_samples_split 
        self.max_depth = max_depth
        
    def build_tree(self, dataset, curr_depth=0):
        
        X, Y = dataset[:,:-1], dataset[:,-1]
        num_samples, num_features = np.shape(X)
        if num_samples>=self.min_samples_split and curr_depth<=self.max_depth:
            best_split = self.get_best_split(dataset, num_samples, num_features)
            if best_split["info_gain"]>0: 
                left_subtree = self.build_tree(best_split["dataset_left"], curr_depth+1)
                right_subtree = self.build_tree(best_split["dataset_right"], curr_depth+1)
                return Node(best_split["feature_index"], best_split["threshold"],
                            left_subtree, right_subtree, best_split["info_gain"])
        

        leaf_value = self.calculate_leaf_value(Y)
        return Node(value=leaf_value)
    
    def get_best_split(self, dataset, num_samples, num_features):
        ''' function to find the best split '''
        
        best_split = {}
        max_info_gain = -float("inf")
        
        for feature_index in range(num_features):
            feature_values = dataset[:, feature_index]
            possible_thresholds = np.unique(feature_values)
            for threshold in possible_thresholds: 
                dataset_left, dataset_right = self.split(dataset, feature_index, threshold)
                if len(dataset_left)>0 and len(dataset_right)>0:
                    y, left_y, right_y = dataset[:, -1], dataset_left[:, -1], dataset_right[:, -1]
                    curr_info_gain = self.information_gain(y, left_y, right_y, "gini")
                    if curr_info_gain>max_info_gain:
                        best_split["feature_index"] = feature_index
                        best_split["threshold"] = threshold
                        best_split["dataset_left"] = dataset_left
                        best_split["dataset_right"] = dataset_right
                        best_split["info_gain"] = curr_info_gain
                        max_info_gain = curr_info_gain
                        
        return best_split
    
    def split(self, dataset, feature_index, threshold):
        dataset_left = np.array([row for row in dataset if row[feature_index]<=threshold])
        dataset_right = np.array([row for row in dataset if row[feature_index]>threshold])
        return dataset_left, dataset_right
    
    def information_gain(self, parent, l_child, r_child, mode="entropy"):
        weight_l = len(l_child) / len(parent)
        weight_r = len(r_child) / len(parent)
        if mode=="gini":
            gain = self.gini_index(parent) - (weight_l*self.gini_index(l_child) + weight_r*self.gini_index(r_child))
        else:
            gain = self.entropy(parent) - (weight_l*self.entropy(l_child) + weight_r*self.entropy(r_child))
        return gain
    
    def entropy(self, y):
        class_labels = np.unique(y)
        entropy = 0
        for cls in class_labels:
            p_cls = len(y[y == cls]) / len(y)
            entropy += -p_cls * np.log2(p_cls)
        return entropy
    
    def gini_index(self, y):
        class_labels = np.unique(y)
        gini = 0
        for cls in class_labels:
            p_cls = len(y[y == cls]) / len(y)
            gini += p_cls**2
        return 1 - gini
        
    def calculate_leaf_value(self, Y):
        
        Y = list(Y)
        return max(Y, key=Y.count)
    
    def print_tree(self, tree=None, indent=" "):
        
        if not tree:
            tree = self.root

        if tree.value is not None:
            print(tree.value)

        else:
            print("X_"+str(tree.feature_index), "<=", tree.threshold, "?", tree.info_gain)
            print("%sleft:" % (indent), end="")
            self.print_tree(tree.left, indent + indent)
            print("%sright:" % (indent), end="")
            self.print_tree(tree.right, indent + indent)
    
    def fit(self, X, Y):
        
        dataset = np.concatenate((X, Y), axis=1)
        self.root = self.build_tree(dataset)
    
    def predict(self, X):
        
        preditions = [self.make_prediction(x, self.root) for x in X]
        return preditions
    
    def make_prediction(self, x, tree):
        
        if tree.value!=None: 
            return tree.value
        feature_val = x[tree.feature_index]
        if feature_val<=tree.threshold:
            return self.make_prediction(x, tree.left)
        else:
            return self.make_prediction(x, tree.right)
        
col_name=['stop_sequence' , 'from_id' , 'to_id' , 'status' , 'line' , 'type' , 'day', 'part_of_the_day' , 'delay']
data = pd.read_csv("NJ_test.csv",skiprows=1, header=None, names=col_name)
X = data.iloc[:, :-1].values
Y = data.iloc[:, -1].values.reshape(-1,1)
X_train, X_test, Y_train, Y_test = train_test_split(X,Y,test_size=.2, random_state=41)

classifier = DecisionTreeClassifier(min_samples_split=3, max_depth=7)
classifier.fit(X_train, Y_train)

Y_pred = classifier.predict(X_test)
print(accuracy_score(Y_test, Y_pred))


#min_samples_split=3, max_depth=1 --> accuracy: 0.7849166666666667
#min_samples_split=1, max_depth=1 --> accuracy: 0.7849166666666667
#min_samples_split=2, max_depth=1 --> accuracy: 0.7849166666666667
#min_samples_split=3, max_depth=2 --> accuracy: 0.7849166666666667
#min_samples_split=3, max_depth=5 --> accuracy: 0.7920833333333334
#min_samples_split=4, max_depth=5 --> accuracy: 0.7920833333333334
#min_samples_split=3, max_depth=6 --> accuracy: 0.7955833333333333
#min_samples_split=3, max_depth=7 --> accuracy: 0.7975833333333333
#min_samples_split=4, max_depth=7 --> accuracy: 0.7975833333333333
#min_samples_split=6, max_depth=7 --> accuracy: 0.7975833333333333
#min_samples_split=7, max_depth=7 --> accuracy: 0.7975833333333333

# min_samples_split és max_depth  értékeinek változtatásával értem el az eredményeket 
# A legnagyobb eredményt  min_samples_split 3 és max_depth 7 értem el 
# az eredményekből akkor értem el jobb változást amikor a depth jóval nagyobb érték volt mint a split. 
# Azonos depth-el és split-el ugyanazt az eredményt kaptam, mint kisebb split-el, de nagyob depth-el
#nehézségek: hosszú futási idők
#Elején sokszor ugyanazt azt eredményeket kaptam így azt hittem, hogy valamit rosszul csináltam 
#Errorokat kaptam pl  min_samples_split 3 és max_depth 8. nál


