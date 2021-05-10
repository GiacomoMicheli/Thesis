from flask import Flask, make_response, send_file, request, json, jsonify
from seaplot import plot
import io


app = Flask(__name__)

# Route
# Check the route to allow the skill use the https protocol
@app.route('/')
def home():
    return "Checked!!"


# Check the existence of the called dataset
@app.route('/data/<name>')
def check_dataset(name):
    try:
        plot.check_data(name)
        speak_output = "The file %s is uploaded" % name
        response = app.response_class(
            response=json.dumps(speak_output),
            status=200,
            mimetype='application/json'
        )
    except:
        speak_output = "I had problems uploading %s. Please repeat file loading process" % name
        response = app.response_class(
            response=json.dumps(speak_output),
            status=500,
            mimetype='application/jason'
        )
    finally:
        return response


# Call the function to generate the plot based on the "plot_type".
# Finally return the Image
@app.route('/genPlot/<path:parameters>/')
def generate_plot(parameters):
    param = parameters_extractor(parameters)
    if param["plot_type"] == "scatter plot":
        image = plot.scatter(param)
    elif param["plot_type"] == "box plot":
        image = plot.box(param)
    elif param["plot_type"] == "bar plot":
        image = plot.bar(param)
    elif param["plot_type"] == "violin plot":
        image = plot.violin(param)
    elif param["plot_type"] == "swarm plot":
        image = plot.swarm(param)
    elif param["plot_type"] == "histogram":
        image = plot.hist(param)
    else:
        image = io.BytesIO()
    image.seek(0)
    response = make_response(send_file(image,
    attachment_filename='plot.png',
    mimetype='image/png'))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


# Check the existence of the encoding type based on the "plot_type"
@app.route("/checkEncoding/<plot_type>/<encoding>/")
def check_encoding(plot_type, encoding):
    scatter_enc = ["color", "shape", "dimension"]
    cat_enc = ["color"]
    hist_enc = ["color"]
    expl_enc = ["color"]
    response = app.response_class (
            status=500,
            mimetype="application/jason"
    )
    if plot_type == "scatter plot":
        if encoding in scatter_enc:
            response = app.response_class (
                status=200,
                mimetype="application/jason"
            )
    elif plot_type == "box plot":
        if encoding in cat_enc:
            response = app.response_class (
                status=200,
                mimetype="application/jason"
            )
    elif plot_type == "bar plot":
        if encoding in cat_enc:
            response = app.response_class (
                status=200,
                mimetype="application/jason"
            )
    elif plot_type == "violin plot":
        if encoding in cat_enc:
            response = app.response_class (
                status=200,
                mimetype="application/jason"
            )
    elif plot_type == "swarm plot":
        if encoding in cat_enc:
            response = app.response_class (
                status=200,
                mimetype="application/jason"
            )
    elif plot_type == "histogram":
        if encoding in hist_enc:
            response = app.response_class (
                status=200,
                mimetype="application/jason"
            )
    elif plot_type == "exploration":
        if encoding in expl_enc:
            response = app.response_class (
                status=200,
                mimetype="application/jason"
            )
    return response


# Check the existence of the variable based on the dataset
@app.route("/checkVariable/<data>/<variable>/")
def checkVar(data, variable):
    if plot.check_existent_var(data.lower(), variable.lower()):
        response = app.response_class (
            status=200,
            mimetype="application/jason"
        )
    else:
        response = app.response_class (
            status=500,
            mimetype="application/jason"
        )
    return response


# Generate the Pair Plot
@app.route("/explore/<path:param>/")
def exploration(param):
    param = parameters_extractor(param)
    image = plot.expl(param)
    image.seek(0)
    response = make_response(send_file(image,
    attachment_filename='plot.png',
    mimetype='image/png'))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


# Return the list of all the available datasets
@app.route("/datasets/")
def show_datasets():
    datasets = plot.datasets()
    res_datasets = {}
    for i in range(len(datasets)):
        res_datasets[i + 1] = datasets[i]
    return app.response_class(
        response=json.dumps(res_datasets),
        status=200,
        mimetype="application/jason"
    )   


# Return the list of all the available variables given the dataset
@app.route("/variables/<data>/")
def show_variables(data):
    data = plot.load_data(data)
    variables = data.columns
    variables_dict = {}
    for index in range(len(variables)):
        single_var = {}
        single_var["primaryText"] = variables[index]
        if (data[variables[index]].dtype == float) or (data[variables[index]].dtype == int):
            single_var["secondaryText"] = "Numerical"
        else:
            single_var["secondaryText"] = "Categorical"
        variables_dict[index + 1] = single_var
    return app.response_class(
        response=json.dumps(variables_dict),
        status=200,
        mimetype="application/jason"
    )


# Function to reconstruct the dictionary starting from the url
def parameters_extractor(param):
    list_of_params = param.split("/")
    params = []
    for p in list_of_params:
        params.append(p.split("="))
    final_struct = {}
    for p in params:
        final_struct[p[0]] = p[1]
    return final_struct


# Starting code
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False, ssl_context='adhoc')
