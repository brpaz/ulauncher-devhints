""" Main Module """

import logging

# pylint: disable=import-error
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, PreferencesEvent, PreferencesUpdateEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction

from ulauncher.config import CACHE_DIR
from devhints import DevHints

LOGGING = logging.getLogger(__name__)


class DevhintsExtension(Extension):
    """ Main Extension Class  """

    def __init__(self):
        """ Initializes the extension """
        super(DevhintsExtension, self).__init__()

        self.devhints_service = DevHints("", LOGGING, CACHE_DIR)

        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent,
                       PreferencesUpdateEventListener())

    def build_result_item(self, page):
        """ Builds a result item object """

        browser_action = OpenUrlAction(page['url'])
        hawkeye_action = RunScriptAction(
            'hawkeye --uri="%s"' % page['url'], [])

        if self.preferences['primary_action'] == "Hawkeye Quicklook":
            on_enter = hawkeye_action
        else:
            on_enter = browser_action

        if self.preferences['secondary_action'] == "None":
            on_alt_enter = DoNothingAction()
        elif self.preferences['secondary_action'] == "Hawkeye Quicklook":
            on_alt_enter = hawkeye_action
        else:
            on_alt_enter = browser_action

        return ExtensionResultItem(icon='images/icon.png',
                                   name=page['name'],
                                   description=page['category'],
                                   on_enter=on_enter,
                                   on_alt_enter=on_alt_enter)


class KeywordQueryEventListener(EventListener):
    """ Listener that handles the user input """

    # pylint: disable=unused-argument,no-self-use
    def on_event(self, event, extension):
        """ Handles the event """
        items = []

        pages = extension.devhints_service.get_cheatsheets_list(
            event.get_argument())

        for page in pages[:10]:
            items.append(extension.build_result_item(page))

        return RenderResultListAction(items)


class PreferencesEventListener(EventListener):
    """
    Listener for prefrences event.
    It is triggered on the extension start with the configured preferences
    """

    def on_event(self, event, extension):
        """ Event handler """
        extension.devhints_service.set_url(event.preferences['url'])


class PreferencesUpdateEventListener(EventListener):
    """
    Listener for "Preferences Update" event.
    It is triggered when the user changes any setting in preferences window
    """

    def on_event(self, event, extension):
        """ Event handler """
        if event.id == 'url':
            extension.devhints_service.set_url(event.new_value)


if __name__ == '__main__':
    DevhintsExtension().run()
