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
from help import sentences

plot_doc_path = "plotDocument.json"

PLOT_TOKEN = "plotToken"

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
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt)
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
            speak_output = res.text + ". Which variable should I put on the horizontal axis?"
        elif res.status_code == 500:
            speak_output = res.text
        else:
            speak_output = "an error occurred"
            
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(sentences.DATA_SELECTED_REPROMPT)
                .response
        )


class SelectXAxisIntentHandler(AbstractRequestHandler):
    """Handler to store the x variable for the plot."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        return ((ask_utils.is_intent_name("SelectXAxisIntent")(handler_input)) &
            ("data" in session_attr))
    
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
            
            return (
                handler_input.response_builder
                    .speak(sentences.AXIS_VARIABLE_STORED.format(xvar, "x", "y"))
                    .ask(sentences.AXIS_VARIABLE_STORED_REPROMPT.format("vertical"))
                    .response
            )


class SelectYAxisIntentHandler(AbstractRequestHandler):
    """Handler to store the y variable for the plot."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        return ((ask_utils.is_intent_name("SelectYAxisIntent")(handler_input)) & 
            ("data" in session_attr))
    
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


class EncodeVariableIntentHandler(AbstractRequestHandler):
    """Handler to encode more variables in the plot."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        return ((ask_utils.is_intent_name("EncodeVariableIntent")(handler_input)) &
        ("xvar" in session_attr) &
        ("yvar" in session_attr)) 
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        session_attr[slots["encoding"].value] = slots["var"].value
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


class EncodeBeforePlotHandler(AbstractRequestHandler):
    """Handler to catch a bad behavior of the user following the path.
    In particular: the user tries to encode variables before having
    created a basic plot"""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        session_attr = handler_input.attributes_manager.session_attributes
        return ((ask_utils.is_intent_name("EncodeVariableIntent")(handler_input)) &
        (("xvar" not in session_attr) |
        ("yvar" not in session_attr)))
    
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
    

class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello World!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
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
sb.add_request_handler(SelectXAxisIntentHandler())
sb.add_request_handler(SelectYAxisIntentHandler())
sb.add_request_handler(UnexpectedPathHanlder())
sb.add_request_handler(EncodeVariableIntentHandler())
sb.add_request_handler(EncodeBeforePlotHandler())
sb.add_request_handler(RemoveEncodingIntentHandler())
sb.add_request_handler(RemoveNonExistentEncoding())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()