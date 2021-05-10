import seaborn as sns
import matplotlib.pyplot as plt
import io

# Return the dataset
def load_data(data):
    datasets = sns.get_dataset_names()
    dataset = select_var(data, datasets)
    return sns.load_dataset(dataset)

# Load the dataset without returning anything
def check_data(data):
    datasets = sns.get_dataset_names()
    dataset = select_var(data, datasets)
    sns.load_dataset(dataset)

# Function to generate the scatter plot
def scatter(param):
    image = io.BytesIO()
    plt.figure(figsize=(8, 6))
    datasets = sns.get_dataset_names()
    data = sns.load_dataset(select_var(param['data'], datasets))
    variables = data.columns
    xvar = select_var(param['xvar'], variables)
    yvar = select_var(param['yvar'], variables)
    color = None
    shape = None
    dim = None
    order = 1
    if 'color' in param:
        color = select_var(param["color"], variables)
    if 'shape' in param:
        shape = select_var(param["shape"], variables)
    if 'dimension' in param:
        dim = select_var(param["dimension"], variables)
    if "order" in param:
        order = int(param["order"])
    if "regression" in param:
        plot = sns.regplot(data=data, x=xvar, y=yvar, order=order)
    else:
        plot = sns.scatterplot(data=data, x=xvar, y=yvar, hue=color, style=shape, size=dim, sizes=(20,200))
    plot.figure.savefig(image, format='png')
    plot.figure.clf()
    plt.close('all')
    return image

# Function to generate the box plot
def box(param):
    plt.figure(figsize=(8, 6))    
    datasets = sns.get_dataset_names()
    data = sns.load_dataset(select_var(param['data'], datasets))
    variables = data.columns
    xvar = select_var(param['xvar'], variables)
    yvar = select_var(param['yvar'], variables)
    color = None
    if "color" in param:
        color = select_var(param["color"], variables)
    plot = sns.boxplot(data=data, x=xvar, y=yvar, hue=color)
    image = io.BytesIO()
    plot.figure.savefig(image, format='png')
    plot.figure.clf()
    plt.close('all')
    return image

# Function to generate the bar plot
def bar(param):
    plt.figure(figsize=(8, 6))
    datasets = sns.get_dataset_names()
    data = sns.load_dataset(select_var(param['data'], datasets))
    variables = data.columns
    xvar = select_var(param['xvar'], variables)
    yvar = select_var(param['yvar'], variables)
    color = None
    if "color" in param:
        color = select_var(param["color"], variables)
    plot = sns.barplot(data=data, x=xvar, y=yvar, hue=color, capsize=.2)
    image = io.BytesIO()
    plot.figure.savefig(image, format='png')
    plot.figure.clf()
    plt.close('all')
    return image

# Function to generate the violin plot
def violin(param):
    plt.figure(figsize=(8, 6))    
    datasets = sns.get_dataset_names()
    data = sns.load_dataset(select_var(param['data'], datasets))
    variables = data.columns
    xvar = select_var(param['xvar'], variables)
    yvar = select_var(param['yvar'], variables)
    color = None
    if "color" in param:
        color = select_var(param["color"], variables)
    plot = sns.violinplot(data=data, x=xvar, y=yvar, hue=color)
    image = io.BytesIO()
    plot.figure.savefig(image, format='png')
    plot.figure.clf()
    plt.close('all')
    return image

# Function to generate the swarm plot
def swarm(param):
    plt.figure(figsize=(8, 6))    
    datasets = sns.get_dataset_names()
    data = sns.load_dataset(select_var(param['data'], datasets))
    variables = data.columns
    xvar = select_var(param['xvar'], variables)
    yvar = select_var(param['yvar'], variables)
    color = None
    if "color" in param:
        color = select_var(param["color"], variables)
    plot = sns.swarmplot(data=data, x=xvar, y=yvar, hue=color)
    image = io.BytesIO()
    plot.figure.savefig(image, format='png')
    plot.figure.clf()
    plt.close('all')
    return image

# Function to generate the histogram
def hist(param):
    plt.figure(figsize=(8, 6))    
    datasets = sns.get_dataset_names()
    data = sns.load_dataset(select_var(param['data'], datasets))
    variables = data.columns
    xvar = select_var(param["xvar"], variables)
    yvar = None
    stat = "count"
    color = None
    kde = False
    if "yvar" in param:
        yvar = select_var(param["yvar"], variables)
    if "stat" in param:
        stat = param["stat"]
    if "color" in param:
        color = select_var(param["color"], variables)
    if "kde" in param:
        kde = True
    plot = sns.histplot(data=data, x=xvar, y=yvar, hue=color, element='step', stat=stat, kde=kde)
    image = io.BytesIO()
    plot.figure.savefig(image, format='png')
    plot.figure.clf()
    plt.close('all')
    return image

# Function to generate the pair plot
def expl(param):    
    datasets = sns.get_dataset_names()
    data = sns.load_dataset(select_var(param['data'], datasets))
    color = None
    if "color" in param:
        color = param["color"]    
    plot = sns.pairplot(data=data, hue=color)
    image = io.BytesIO()
    plot.savefig(image, format='png')
    plt.close()
    return image

# Function to select the variable based on Hamming's distance
def select_var(var, variables):
    selected_var = None
    distance = float("inf")
    for v in variables:
        d = dist(var, v)
        if d < distance:
            distance = d
            selected_var = v
    return selected_var

# Function to compute the Hamming's distance
def dist(s1, s2):
    s1 = only_char(list(s1.lower()))
    s2 = only_char(list(s2.lower()))
    d = 0
    while len(s1) < len(s2):
        s1.append("-")
    while len(s2) < len(s1):
        s2.append("-")
    for i in range(len(s1)):
        if s1[i] != s2[i]:
            d += 1
    return d

# Function to remove every special caracter
def only_char(s):
    valid_char = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
        "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    for c in s:
        if c not in valid_char:
            s.remove(c)
    return s

# Function to check if a variable exists
def check_existent_var(data, var):
    data = sns.load_dataset(data)
    var = only_char(list(var))
    list_of_vars = []
    for v in data.columns:
        list_of_vars.append(only_char(list(v)))
    if var in list_of_vars:
        return True
    else:
        return False

# Function to return all the available dataset names
def datasets():
    return sns.get_dataset_names()