# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []


from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker , FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, Form 
from rasa_sdk.types import DomainDict
import datetime as dt 
import requests
from news_action import NewsFromBBC
from rasa_sdk import ActionExecutionRejection
from rasa_sdk.events import SlotSet
from rasa_sdk.forms import FormAction, REQUESTED_SLOT, Action

#####################################################################################################################################
#checking the entity values 

class ActionCheckslotvalues(Action):

     def name(self) -> Text:
        return "action_check_slot_values"

     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any])  -> List[Dict[Text, Any]]:
             user = tracker.get_slot("user")
             if user is  None:
                 return[dispatcher.utter_message(response= "utter_new_user" ) ]
            
             else:
                  return [dispatcher.utter_message(response="utter_welcomeback",User=tracker.get_slot("user"))]
#####################################################################################################################################
#validation of name ie name cannot be less than 2 letters
                   
class ValidateNameForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_name_form"

    def validate_user(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `user` value."""

        # If the name is super short, it might be wrong.
        print(f"First name given = {slot_value} length = {len(slot_value)}")
        if len(slot_value) <= 2:
            dispatcher.utter_message(text=f"That's a very short name. I'm assuming you mis-spelled.")
            return {"user": None}
        else:
            return {"user": slot_value}  
#####################################################################################################################################
#actions primary

class ActionIambot(Action):
     def name(self) -> Text:
        return "action_iambot"

     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
             dispatcher.utter_message(text=" I am a bot, powered by Rasa,trained to help you.")
             return [] 

class ActionCheerUp(Action):
     def name(self) -> Text:
        return "action_cheerup"

     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
             Link = "https://i.imgur.com/nGF1K8f.jpg"
             dispatcher.utter_message(response="utter_cheer_up",link=Link)
             return []

class ActionMustCheerUp(Action):
     def name(self) -> Text:
        return "action_mustcheerup"

     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
             Link = "https://www.youtube.com/watch?v=nvzkHGNdtfk&ab_channel=CentralPerk"
             dispatcher.utter_message(response="utter_verysad",link=Link)
             return []

class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_show_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text=f"{dt.datetime.now()}")

        return []
#####################################################################################################################################
#corona state action

class Actioncoronastats(Action):

    def name(self) -> Text:
        return "action_corona_state_stat"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        responses = requests.get("https://api.covid19india.org/data.json").json()

        entities = tracker.latest_message['entities']
        print("Now Showing Data For:", entities)
        state = None

        for i in entities:
            if i["entity"] == "state":
                state = i["value"]

        message = "Please Enter Correct State Name !"

        if state == "india":
            state = "Total"
        for data in responses["statewise"]:
            if data["state"] == state.title():
                print(data)
                message = "Now Showing Cases For --> " + state.title() + " Since Last 24 Hours : "+ "\n" + "Active: " + data[
                    "active"] + " \n" + "Confirmed: " + data["confirmed"] + " \n" + "Recovered: " + data[
                              "recovered"] + " \n" + "Deaths: " + data["deaths"] + " \n" + "As Per Data On: " + data[
                              "lastupdatedtime"]

        print(message)
        dispatcher.utter_message(message)

        return []

#####################################################################################################################################
#random news action


NEWS_API_KEY = '6a829855bda14b179c725bcc5fc33267'  


class topic_related(FormAction):
    def name(self):
        return "action_get_news"
    
    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["topic_news"]

    def slot_mappings(self):
        return {"topic_news": [self.from_text(intent=[None, "topic_related", "inform"]), 
                               self.from_entity(entity="topic_news", intent =["topic_related"])]}

    def validate(self,
                 dispatcher: CollectingDispatcher,
                 tracker: Tracker,
                 domain: Dict[Text, Any]) -> List[Dict]:

        slot_values = self.extract_other_slots(dispatcher, tracker, domain)
        
        # extract requested slot
        slot_to_fill = tracker.get_slot(REQUESTED_SLOT)
        if slot_to_fill:
            slot_values.update(self.extract_requested_slot(dispatcher, tracker, domain))
            if not slot_values:
                # reject form action execution
                # if some slot was requested but nothing was extracted
                # it will allow other policies to predict another action
                raise ActionExecutionRejection(self.name(),
                                               "Failed to validate slot {0} "
                                               "with action {1}"
                                               "".format(slot_to_fill,
                                                         self.name()))

        # we'll check when validation failed in order
        # to add appropriate utterances
    

        # validation succeed, set the slots values to the extracted values
        return [SlotSet(slot, value) for slot, value in slot_values.items()]

    def submit(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict]:

        """Define what the form has to do
            after all required slots are filled"""

        topic_news = tracker.get_slot("topic_news")
        
        pageSize = '6' # Set the number to how many news articles you want to fetch 
        
        url = "https://newsapi.org/v2/everything?q=" + topic_news + "&apiKey=" + NEWS_API_KEY + "&pageSize=" + pageSize
        
        r = requests.get(url = url)
        data = r.json() # extracting data in json format
        data = data['articles']

        dispatcher.utter_message("Here is some news I found!")

        for i in range(len(data)):
            output = data[i]['title'] + "\n" + data[i]['url'] + "\n"
            dispatcher.utter_message(output)

        dispatcher.utter_template("utter_confirm_if_service_is_correct", tracker)

        # utter submit template
        return []

#####################################################################################################################################
# specific news action

class ActionNewsTracker(Action):
    def name(self) -> Text:
        return "action_news_tracker"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            message = NewsFromBBC()
            
            dispatcher.utter_message(text=message)

        except:
            m = "Sorry your request could not be processed.There maybe some problem with the server."
            dispatcher.utter_message(text=m)

        return []


#####################################################################################################################################


