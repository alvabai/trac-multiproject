# -*- coding: utf-8 -*-
"""
Messages module contains the Trac components for providing messaging service to setup:

- api: Provides REST API handlers for sending and receiving messages
- notify: Listens the relevant service notifications and sends messages from them
- ui: Contains UI components for showing and sending messages
- admin: Contains UI components for administrative pages

"""
from multiproject.common.messages.api import MessageRestAPI, MessageService
from multiproject.common.messages.admin import MessagesAdminPanel
from multiproject.common.messages.ui import MessagesDialog, MessagesGroupBox

