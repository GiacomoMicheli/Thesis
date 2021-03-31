WELCOME_MESSAGE = "Welcome in plot me, I'm here to plot your data! Please, tell me the name of the file with your data"
WELCOME_REPROMPT = "To begin, I need to know the name of the file you want to use"

SERVER = "https://ec2-15-161-104-205.eu-south-1.compute.amazonaws.com:5000/"

DATA_BEFORE_AXES = "You did not open any file yet."
DATA_BEFORE_AXES_REPROMPT = "please, open the file with the data"

DATA_SELECTED_REPROMPT = "It's time to select the variable for the axes!"

AXIS_VARIABLE_STORED = "I am using the variable {} on the {} axis. What is the variable for the {} axis?"
AXIS_VARIABLE_STORED_REPROMPT = "Please, tell the name of the variable for the {} axis"

BASIC_PLOT_SPEAK = "Here we are! You should be able to see the plot now. Let me know if you want to encode more variables."
BASIC_PLOT_REPROMPT = "Tell me if you want to encode more variables in your plot."

ENCODING_SPEAK = "I have encoded {}. If you need to make more changes I am here for this."
ENCODING_REPROMPT = "Tell me what are the changes you need to make."

REMOVE_ENCODING_SPEAK = "I have eliminated the variable encoded in the {}."
REMOVE_ENCODING_REPROMPT = "Tell me if you need something more."

ENCODING_BEFORE_PLOT_SPEAK = "Ehi! Let's create a basic plot before encoding more variables"
ENCODING_BEFORE_PLOT_REPROMPT = "C'mon! Let's finish the basic plot"

REMOVE_NON_EXISTING_ENCODING = "You haven't encoded anything yet in {}"
REMOVE_NON_EXISTING_ENCODING_REPROMPT = "You need to encode something before"

REMOVE_ALL_ENCODINGS = "Now you are back at the basic plot."
REMOVE_ALL_ENCODINGS_REPROMPT = "You can see the basic plot. Tell me what you want to do next"

PLOT_TYPE_SPEAK = "Ok, let's do this {}. Which variable should I put on the horizontal axis?"
PLOT_TYPE_REPROMPT = "Now I need to know the variable for the abscissa"

TYPE_BEFORE_AXES = "Before select the variables for the axes you must tell me the type of plot you need"
TYPE_BEFORE_AXES_REPROMPT = "Tell me the type of plot you need before going on"

NON_VALID_ENCODING = "In this type of plot it is not possible to encode variables in the {}"
NON_VALID_ENCODING_REPROMPT = "Try to encode somehow else"