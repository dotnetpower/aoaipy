# https://github.com/microsoft/BotBuilder-Samples/blob/main/samples/python/81.skills-skilldialog/dialog-skill-bot/app.py
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from http import HTTPStatus

from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    ConversationState,
    MemoryStorage,
    UserState,
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.integration.aiohttp import ConfigurationBotFrameworkAuthentication
from botbuilder.schema import Activity
from botframework.connector.auth import AuthenticationConfiguration

from authentication import AllowedCallersClaimsValidator
from bots import AoaiBot
from config import DefaultConfig

# from dialogs import ActivityRouterDialog, DialogSkillBotRecognizer
from skill_adapter_with_error_handler import AdapterWithErrorHandler
import logging, json
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

CONFIG = DefaultConfig()

# Create MemoryStorage, UserState and ConversationState
MEMORY = MemoryStorage()
USER_STATE = UserState(MEMORY)
CONVERSATION_STATE = ConversationState(MEMORY)

# Create adapter.
# See https://aka.ms/about-bot-adapter to learn more about how bots work.
VALIDATOR = AllowedCallersClaimsValidator(CONFIG).claims_validator

SETTINGS = ConfigurationBotFrameworkAuthentication(
    CONFIG,
    auth_configuration=AuthenticationConfiguration(claims_validator=VALIDATOR),
)
ADAPTER = AdapterWithErrorHandler(SETTINGS, CONVERSATION_STATE)

# Create the Bot
BOT = AoaiBot(conversation_state=CONVERSATION_STATE, user_state=USER_STATE, config=CONFIG)

# Listen for incoming requests on /api/messages
async def messages(req: Request) -> Response:
    # Main bot message handler.
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    print(json.dumps(body, indent=4))
    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    invoke_response = await ADAPTER.process_activity(auth_header, activity, BOT.on_turn)
    if invoke_response:
        return json_response(data=invoke_response.body, status=invoke_response.status)
    return Response(status=HTTPStatus.OK)


APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    try:
        web.run_app(APP, host="localhost", port=CONFIG.PORT)
        
    except Exception as error:
        raise error