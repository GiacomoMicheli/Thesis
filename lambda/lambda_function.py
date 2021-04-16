# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import requests
import utils
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import (Response, Intent)
from ask_sdk_model.dialog import ElicitSlotDirective
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective

from typing import Dict, Any
from static_speak import sentences

expl_doc_path = "APL_documents/explorationDocument.json"
plot_doc_path = "APL_documents/plotDocument.json"
list_doc_path = "APL_documents/listDocument.json"

EXPL_TOKEN = "explToken"
PLOT_TOKEN = "plotToken"
LIST_TOKEN = "listToken"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = sentences.WELCOME_MESSAGE
        reprompt = sentences.WELCOME_REPROMPT
        url = sentences.SERVER + "datasets/"
        
        res = requests.get(url, verify=False)
        
        if res.status_code == 200:
            datasets_dict = res.json()
            list_of_datasets = []
            for value in datasets_dict.values():
                item = {}
                item["primaryText"] = value
                list_of_datasets.append(item)
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(reprompt)
                    .add_directive(
                        RenderDocumentDirective(
                            token=LIST_TOKEN,
                            document=utils._load_apl_document(list_doc_path),
                            datasources={
                                'datasets': {
                                    'type': 'object',
                                    'properties': {
                                        'title': 'Available datasets',
                                        'available_datasets': list_of_datasets
                                    }
                                }
                            }
                        ))
                    .response
            )
        else:
            return (
                handler_input.response_builder
                    .speak("I had problems contacting the server")
                    .response
            )


class SelectDataIntentHandler(AbstractRequestHandler):
    """Handler to store the name of the file with the data."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("SelectDataIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        # Reset session attributes when a new file has to be opened
        handler_input.attributes_manager.session_attributes = {}
        
        # Get the value of the file name from the slot and store it in the session attributes
        data = handler_input.request_envelope.request.intent.slots["data"].value
        session_attr = handler_input.attributes_manager.session_attributes
        
        # Generate the url to test the existence of the file
        url = utils.test_data_existence(sentences.SERVER, data)

        res = requests.get(url, verify=False)
        if res.status_code == 200:
            session_attr["data"] = data
            speak_output = res.text + ". Please, tell me the type of plot you want to draw"
        elif res.status_code == 500:
            speak_output = res.text
        else:
            speak_output = "an error occurred"
            
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class ExplorationIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        return ((ask_utils.is_intent_name("ExplorationIntent")(handler_input)) and
        ("data" in session_attr))
    
    def handle(self, handler_input):
        data = handler_input.attributes_manager.session_attributes["data"]
        handler_input.attributes_manager.session_attributes = {}
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["data"] = data
        session_attr["plot_type"] = "exploration"
        image_link = utils.generate_url_exploration(sentences.SERVER, session_attr)
        
        return (
            handler_input.response_builder
                .speak("Here we are. You should be able to see the plot!")
                .ask("Check the plot on your screen")
                .add_directive(
                    RenderDocumentDirective(
                        token=EXPL_TOKEN,
                        document=utils._load_apl_document(expl_doc_path),
                        datasources={
                            'image_data': {
                                'type': 'object',
                                'properties': {
                                    'image': image_link
                                }
                            }
                        }
                    ))
                .response
        )


class SelectPlotIntentHandler(AbstractRequestHandler):
    """Handler to select the type of plot to do."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        return ((ask_utils.is_intent_name("SelectPlotIntent")(handler_input)) &
        ("data" in session_attr))
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        data = handler_input.attributes_manager.session_attributes["data"]
        plot_type = handler_input.request_envelope.request.intent.slots["plot"].value
        handler_input.attributes_manager.session_attributes = {}
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["plot_type"] = plot_type
        session_attr["data"] = data
        
        url_var = sentences.SERVER + "variables/" + data + "/"
        res_var = requests.get(url_var, verify=False)
        if res_var.status_code == 200:
            variables_dict = res_var.json()
            list_of_vars = []
            for value in variables_dict.values():
                list_of_vars.append(value)
            return (
                handler_input.response_builder                
                    .speak(sentences.PLOT_TYPE_SPEAK.format(plot_type))
                    .ask(sentences.PLOT_TYPE_REPROMPT)
                    .add_directive(
                        RenderDocumentDirective(
                            token=LIST_TOKEN,
                            document=utils._load_apl_document(list_doc_path),
                            datasources={
                                'datasets': {
                                    'type': 'object',
                                    'properties': {
                                        'title': 'Available variables',
                                        'available_datasets': list_of_vars
                                    }
                                }
                            }
                        ))
                    .response
                )
        else:
            return (
                handler_input.response_builder
                    .speak("An error occured")
                    .response
                )


class SelectXAxisIntentHandler(AbstractRequestHandler):
    """Handler to store the x variable for the plot."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        return ((ask_utils.is_intent_name("SelectXAxisIntent")(handler_input)) &
            ("data" in session_attr) &
            ("plot_type" in session_attr))
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attr = handler_input.attributes_manager.session_attributes
        xvar = handler_input.request_envelope.request.intent.slots["xvar"].value
        
        if "yvar" in session_attr:
            session_attr["xvar"] = xvar
            image_link = utils.generate_url_plot(sentences.SERVER, session_attr)
            
            return (
                handler_input.response_builder
                    .speak("Here we are. You should be able to see the plot!")
                    .ask("Check the plot on your screen")
                    .add_directive(
                        RenderDocumentDirective(
                            token=PLOT_TOKEN,
                            document=utils._load_apl_document(plot_doc_path),
                            datasources={
                                'image_data': {
                                    'type': 'object',
                                    'properties': {
                                        'title': 'Here the plot',
                                        'image': image_link
                                    }
                                }
                            }
                        ))
                    .response
            )
        else:
            session_attr["xvar"] = xvar
            if session_attr["plot_type"] != "histogram":
                return (
                    handler_input.response_builder
                        .speak(sentences.AXIS_VARIABLE_STORED.format(xvar, "x", "y"))
                        .ask(sentences.AXIS_VARIABLE_STORED_REPROMPT.format("vertical"))
                        .response
                )
            else:
                return (
                    handler_input.response_builder
                        .speak(sentences.X_AXIS_STORED.format(xvar))
                        .ask(sentences.X_STORED_REPROMPT)
                        .response
                    )


class SelectYAxisIntentHandler(AbstractRequestHandler):
    """Handler to store the y variable for the plot."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        return ((ask_utils.is_intent_name("SelectYAxisIntent")(handler_input)) & 
            ("data" in session_attr) &
            ("plot_type" in session_attr))
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attr = handler_input.attributes_manager.session_attributes
        yvar = handler_input.request_envelope.request.intent.slots["yvar"].value
        
        if "xvar" in session_attr:
            session_attr["yvar"] = yvar
            image_link = utils.generate_url_plot(sentences.SERVER, session_attr)
            
            return (
                handler_input.response_builder
                    .speak(sentences.BASIC_PLOT_SPEAK)
                    .ask(sentences.BASIC_PLOT_REPROMPT)
                    .add_directive(
                        RenderDocumentDirective(
                            token=PLOT_TOKEN,
                            document=utils._load_apl_document(plot_doc_path),
                            datasources={
                                'image_data': {
                                    'type': 'object',
                                    'properties': {
                                        'title': 'Here the plot',
                                        'image': image_link
                                    }
                                }
                            }
                        ))
                    .response
            )
        else:
            session_attr["yvar"] = yvar
            
            return (
                handler_input.response_builder
                    .speak(sentences.AXIS_VARIABLE_STORED.format(yvar, "y", "x"))
                    .ask(sentences.AXIS_VARIABLE_STORED_REPROMPT.format("horizontal"))
                    .response
            )


class SelectStatIntentHandler(AbstractRequestHandler):
    """Handler to store the aggregate statistic for each bin in histograms."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        return ((ask_utils.is_intent_name("SelectStatIntent")(handler_input)) & 
            ("data" in session_attr) &
            ("plot_type" in session_attr))
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attr = handler_input.attributes_manager.session_attributes
        stat = handler_input.request_envelope.request.intent.slots["stat"].value
        
        if session_attr["plot_type"] != "histogram":
            return (
                handler_input.response_builder
                    .speak("You can't add the aggregate statistic to this type of plot")
                    .ask("try with something else")
                    .response
                )
        elif "xvar" not in session_attr:
            session_attr["stat"] = stat
            return (
                handler_input.response_builder
                    .speak(sentences.STAT_STORED.format(stat))
                    .ask("What variable should I use on the abscissa?")
                    .response
                )
        else:
            session_attr["stat"] = stat
            image_link = utils.generate_url_plot(sentences.SERVER, session_attr)
            
            return (
                handler_input.response_builder
                    .speak(sentences.BASIC_PLOT_SPEAK)
                    .ask(sentences.BASIC_PLOT_REPROMPT)
                    .add_directive(
                        RenderDocumentDirective(
                            token=PLOT_TOKEN,
                            document=utils._load_apl_document(plot_doc_path),
                            datasources={
                                'image_data': {
                                    'type': 'object',
                                    'properties': {
                                        'title': 'Here the plot',
                                        'image': image_link
                                    }
                                }
                            }
                        ))
                    .response
            )


class UnexpectedPathHanlder(AbstractRequestHandler):
    """Handler to catch a bad behavior of the user following the path.
    In particular: if the user tries to select variables for the axes before
    selecting the data to open."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        return ((not(ask_utils.is_intent_name("SelectDataIntent")(handler_input))) &
            ("data" not in session_attr))
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return (
            handler_input.response_builder
                .speak(sentences.DATA_BEFORE_AXES)
                .ask(sentences.DATA_BEFORE_AXES_REPROMPT)
                .add_directive(
                    directive=ElicitSlotDirective(
                        updated_intent=Intent(
                            name='SelectDataIntent'),
                        slot_to_elicit='data'))
                .response
        )


class EncodingVariableExploration(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        return ((ask_utils.is_intent_name("EncodeVariableIntent")(handler_input)) and
        (session_attr["plot_type"] == "exploration"))
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        url_enc = sentences.SERVER + "checkEncoding/" + session_attr["plot_type"] + "/" + slots["encoding"].value + "/"
        url_var = sentences.SERVER + "checkVariable/" + session_attr["data"] + "/" + slots["var"].value + "/"
        res_enc = requests.get(url_enc, verify=False)
        res_var = requests.get(url_var, verify=False)
        
        if (res_enc.status_code == 200) and (res_var.status_code == 200):
            session_attr[slots["encoding"].value] = slots["var"].value
            image_link = utils.generate_url_exploration(sentences.SERVER, session_attr)
            return (
                handler_input.response_builder
                    .speak(sentences.ENCODING_SPEAK.format(slots["var"].value))
                    .ask(sentences.ENCODING_REPROMPT)
                    .add_directive(
                        RenderDocumentDirective(
                            token=EXPL_TOKEN,
                            document=utils._load_apl_document(expl_doc_path),
                            datasources={
                                'image_data': {
                                    'type': 'object',
                                    'properties': {
                                        'image': image_link
                                    }
                                }
                            }
                        ))
                    .response
            )


class RemoveEncodingExploration(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        return ((ask_utils.is_intent_name("RemoveEncodingIntent")(handler_input)) and
        (slots["encoding"].value in session_attr) and
        (session_attr["plot_type"] == "exploration"))
    
    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        del session_attr[slots["encoding"].value]
        image_link = utils.generate_url_exploration(sentences.SERVER, session_attr)
        return (
            handler_input.response_builder
                .speak(sentences.REMOVE_ENCODING_SPEAK.format(slots["encoding"].value))
                .ask(sentences.REMOVE_ENCODING_REPROMPT)
                .add_directive(
                    RenderDocumentDirective(
                        token=EXPL_TOKEN,
                        document=utils._load_apl_document(expl_doc_path),
                        datasources={
                            'image_data': {
                                'type': 'object',
                                'properties': {
                                    'image': image_link
                                }
                            }
                        }
                    ))
                .response
            )


class AxisBeforeTypeHandler(AbstractRequestHandler):
    """Handler to catch a bad behavior of the user following the path.
    In particular: The user tries to select the variables before chosing
    the plot type"""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        return ((not(ask_utils.is_intent_name("SelectPlotIntent")(handler_input))) &
        (("plot_type" not in session_attr) or
        (session_attr["plot_type"] == "exploration")))
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return (
            handler_input.response_builder
                .speak(sentences.TYPE_BEFORE_AXES)
                .ask(sentences.TYPE_BEFORE_AXES_REPROMPT)
                .response
            )


class ShowRegressionIntentHandler(AbstractRequestHandler):
    """Handler to plot the regression line."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        return ((ask_utils.is_intent_name("ShowRegressionIntent")(handler_input)) &
        ("xvar" in session_attr) and
        ("yvar" in session_attr) and
        (session_attr["plot_type"] == "scatter plot"))
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attr = handler_input.attributes_manager.session_attributes
        if ("color" in session_attr) or ("dimension" in session_attr) or ("shape" in session_attr):
            return (
                handler_input.response_builder
                    .speak("To plot the regression line you need to remove other encodings")
                    .response
                )
        else:
            slots = handler_input.request_envelope.request.intent.slots
            session_attr["regression"] = "yes"
            if slots["order"].value:
                session_attr["order"] = slots["order"].value
            image_link = utils.generate_url_plot(sentences.SERVER, session_attr)
            return (
                handler_input.response_builder
                    .speak("Here the regression line!")
                    .ask("Now you can see the regression line")
                    .add_directive(
                        RenderDocumentDirective(
                            token=PLOT_TOKEN,
                            document=utils._load_apl_document(plot_doc_path),
                            datasources={
                                'image_data': {
                                    'type': 'object',
                                    'properties': {
                                        'title': 'Here the plot',
                                        'image': image_link
                                    }
                                }
                            }
                        ))
                    .response
            )


class RegressionBeforePlotHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        return ((ask_utils.is_intent_name("ShowRegressionIntent")(handler_input)) and
        (("xvar" not in session_attr) or
        (("yvar" not in session_attr) and
        ("stat" not in session_attr))))
    
    def handle(self, handler_input):
        return (
            handler_input.response_builder
                .speak("Let's finish the basic plot before")
                .response
        )


class RegressionOnWrongPlot(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        return ((ask_utils.is_intent_name("ShowRegressionIntent")(handler_input)) and
        (session_attr["plot_type"] != "scatter plot"))
    
    def handle(self, handler_input):
        return (
            handler_input.response_builder
                .speak("The regression line can be shown only on a scatter plot")
                .response
            )


class RemoveRegressionIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        return ((ask_utils.is_intent_name("RemoveRegressionIntent")(handler_input)) and
        ("regression" in session_attr))
    
    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        del session_attr["regression"]
        if "order" in session_attr:
            del session_attr["order"]
        image_link = utils.generate_url_plot(sentences.SERVER, session_attr)
        return (
            handler_input.response_builder
                .speak("I removed the regression line!")
                .add_directive(
                    RenderDocumentDirective(
                        token=PLOT_TOKEN,
                        document=utils._load_apl_document(plot_doc_path),
                        datasources={
                            'image_data': {
                                'type': 'object',
                                'properties': {
                                    'title': 'Here the plot',
                                    'image': image_link
                                }
                            }
                        }
                    ))
                .response
        )


class RemoveNonExistentRegression(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        return ((ask_utils.is_intent_name("RemoveRegressionIntent")(handler_input)) and
        ("regression" not in session_attr))
    
    def handle(self, handler_input):
        return (
            handler_input.response_builder
                .speak("There is no regression line to remove")
                .response
        )


class KernelDensityIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        return ((ask_utils.is_intent_name("KernelDensityIntent")(handler_input)) &
        ("xvar" in session_attr) and
        (("yvar" in session_attr) or
        ("stat" in session_attr)) and
        (session_attr["plot_type"] == "histogram"))
    
    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["kde"] = "yes"
        image_link = utils.generate_url_plot(sentences.SERVER, session_attr)
        return (
            handler_input.response_builder
                    .speak("Here the kernel density estimation!")
                    .ask("Now you can see the kernel density estimation")
                    .add_directive(
                        RenderDocumentDirective(
                            token=PLOT_TOKEN,
                            document=utils._load_apl_document(plot_doc_path),
                            datasources={
                                'image_data': {
                                    'type': 'object',
                                    'properties': {
                                        'title': 'Here the plot',
                                        'image': image_link
                                    }
                                }
                            }
                        ))
                    .response
        )


class KernelDensityBeforePlot(AbstractRequestHandler):
    """Handler to catch a bad behavior of the user following the path.
    In particular: the user tries to add the kernel density estimation before
    having a basic plot"""
    def can_handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        return ((ask_utils.is_intent_name("KernelDensityIntent")(handler_input)) and
        (("xvar" not in session_attr) or
        (("yvar" not in session_attr) and
        ("stat" not in session_attr))))
    
    def handle(self, handler_input):
        return (
            handler_input.response_builder
                .speak("Let's finish the basic plot before")
                .response
        )


class KernelDensityWrongPlot(AbstractRequestHandler):
    """Handler to catch a bad behavior of the user following the path.
    In Particular: the user tries to plot the kernel density estimation on
    a plot different from a histogram"""
    def can_handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        return ((ask_utils.is_intent_name("KernelDensityIntent")(handler_input)) and
        (session_attr["plot_type"] != "histogram"))
    
    def handle(self, handler_input):
        return (
            handler_input.response_builder
                .speak("The kernel density estimation can be shown only on a histogram")
                .response
        )


class RemoveKernelIntentHandler(AbstractRequestHandler):
    """Handler to remove the kernel estimation density from the plot."""
    def can_handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        return ((ask_utils.is_intent_name("RemoveKernelIntent")(handler_input)) and
        ("kde" in session_attr))
    
    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        del session_attr["kde"]
        image_link = utils.generate_url_plot(sentences.SERVER, session_attr)
        return (
            handler_input.response_builder
                .speak("I removed the kernel density estimation!")
                .add_directive(
                    RenderDocumentDirective(
                        token=PLOT_TOKEN,
                        document=utils._load_apl_document(plot_doc_path),
                        datasources={
                            'image_data': {
                                'type': 'object',
                                'properties': {
                                    'title': 'Here the plot',
                                    'image': image_link
                                }
                            }
                        }
                    ))
                .response
        )


class RemoveNonExistentKernelDensity(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        return ((ask_utils.is_intent_name("RemoveKernelIntent")(handler_input)) and
        ("kde" not in session_attr))
    
    def handle(self, handler_input):
        return (
            handler_input.response_builder
                .speak("There is no kernel density estimation to remove")
                .response
        )


class EncodeVariableIntentHandler(AbstractRequestHandler):
    """Handler to encode more variables in the plot."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        return ((ask_utils.is_intent_name("EncodeVariableIntent")(handler_input)) &
        ("xvar" in session_attr) &
        (("yvar" in session_attr) or
        ("stat" in session_attr)))
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        url_enc = sentences.SERVER + "checkEncoding/" + session_attr["plot_type"] + "/" + slots["encoding"].value + "/"
        url_var = sentences.SERVER + "checkVariable/" + session_attr["data"] + "/" + slots["var"].value + "/"
        res_enc = requests.get(url_enc, verify=False)
        res_var = requests.get(url_var, verify=False)
        
        if (res_enc.status_code == 200) and (res_var.status_code == 200):
            session_attr[slots["encoding"].value] = slots["var"].value
            if "regression" in session_attr:
                return (
                    handler_input.response_builder
                        .speak("To encode variables you need to remove the regression line")
                        .response
                )
            else:
                image_link = utils.generate_url_plot(sentences.SERVER, session_attr)
                return (
                handler_input.response_builder
                    .speak(sentences.ENCODING_SPEAK.format(slots["var"].value))
                    .ask(sentences.ENCODING_REPROMPT)
                    .add_directive(
                        RenderDocumentDirective(
                            token=PLOT_TOKEN,
                            document=utils._load_apl_document(plot_doc_path),
                            datasources={
                                'image_data': {
                                    'type': 'object',
                                    'properties': {
                                        'title': 'Here the plot',
                                        'image': image_link
                                    }
                                }
                            }
                        ))
                    .response
                )
        elif (res_enc.status_code == 500):
            return (
                handler_input.response_builder
                    .speak(sentences.NON_VALID_ENCODING.format(slots["encoding"].value))
                    .ask(sentences.NON_VALID_ENCODING_REPROMPT)
                    .response
            )
        elif (res_var.status_code == 500):
            return (
                handler_input.response_builder
                    .speak(sentences.INEXISTENT_VAR.format(slots["var"].value))
                    .ask(sentences.INEXISTENT_VAR_REPROMPT)
                    .response
            )
        else:
            return (
                handler_input.response_builder
                    .speak("An error occured")
                    .ask("I am sorry, but I have problems doing this part")
                    .response
            )


class EncodeBeforePlotHandler(AbstractRequestHandler):
    """Handler to catch a bad behavior of the user following the path.
    In particular: the user tries to encode variables before having
    created a basic plot"""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        return ((ask_utils.is_intent_name("EncodeVariableIntent")(handler_input)) &
        (((("xvar" not in session_attr) or
        (("yvar" not in session_attr) and
        ("stat" not in session_attr)))) and
        (session_attr["plot_type"] != "exploration")))
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return (
            handler_input.response_builder
                .speak(sentences.ENCODING_BEFORE_PLOT_SPEAK)
                .ask(sentences.ENCODING_BEFORE_PLOT_REPROMPT)
                .response
        )


class RemoveEncodingIntentHandler(AbstractRequestHandler):
    """Handler to eliminate one encoding."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        return ((ask_utils.is_intent_name("RemoveEncodingIntent")(handler_input)) &
        (slots["encoding"].value in session_attr))
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        del session_attr[slots["encoding"].value]
        image_link = utils.generate_url_plot(sentences.SERVER, session_attr)
        return (
        handler_input.response_builder
            .speak(sentences.REMOVE_ENCODING_SPEAK.format(slots["encoding"].value))
            .ask(sentences.REMOVE_ENCODING_REPROMPT)
            .add_directive(
                RenderDocumentDirective(
                    token=PLOT_TOKEN,
                    document=utils._load_apl_document(plot_doc_path),
                    datasources={
                        'image_data': {
                            'type': 'object',
                            'properties': {
                                'title': 'Here the plot',
                                'image': image_link
                            }
                        }
                    }
                ))
            .response
        )


class RemoveNonExistentEncoding(AbstractRequestHandler):
    """Handler to catch a bad behavior of the user following the path.
    In particular: the user tries to remove an encoding which does not esits."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        return ((ask_utils.is_intent_name("RemoveEncodingIntent")(handler_input)) &
        (slots["encoding"].value not in session_attr))
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        image_link = utils.generate_url_plot(sentences.SERVER, session_attr)
        return (
            handler_input.response_builder
                .speak(sentences.REMOVE_NON_EXISTING_ENCODING.format(slots["encoding"].value))
                .ask(sentences.REMOVE_NON_EXISTING_ENCODING_REPROMPT)
                .response
            )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(SelectDataIntentHandler())
sb.add_request_handler(ExplorationIntentHandler())
sb.add_request_handler(EncodingVariableExploration())
sb.add_request_handler(RemoveEncodingExploration())
sb.add_request_handler(SelectPlotIntentHandler())
sb.add_request_handler(AxisBeforeTypeHandler())
sb.add_request_handler(SelectXAxisIntentHandler())
sb.add_request_handler(SelectYAxisIntentHandler())
sb.add_request_handler(SelectStatIntentHandler())
sb.add_request_handler(UnexpectedPathHanlder())
sb.add_request_handler(EncodeVariableIntentHandler())
sb.add_request_handler(ShowRegressionIntentHandler())
sb.add_request_handler(RegressionBeforePlotHandler())
sb.add_request_handler(RegressionOnWrongPlot())
sb.add_request_handler(RemoveRegressionIntentHandler())
sb.add_request_handler(RemoveNonExistentRegression())
sb.add_request_handler(KernelDensityIntentHandler())
sb.add_request_handler(KernelDensityBeforePlot())
sb.add_request_handler(KernelDensityWrongPlot())
sb.add_request_handler(RemoveKernelIntentHandler())
sb.add_request_handler(RemoveNonExistentKernelDensity())
sb.add_request_handler(EncodeBeforePlotHandler())
sb.add_request_handler(RemoveEncodingIntentHandler())
sb.add_request_handler(RemoveNonExistentEncoding())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()