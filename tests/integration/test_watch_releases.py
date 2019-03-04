# # -*- coding: utf-8 -*-
"""
test command watch-releases
"""
from packit.bot_api import PackitBotAPI
from packit.config import Config


def test_single_message():
    # https://apps.fedoraproject.org/datagrepper/id?id=2019-825aeb79-2681-4572-8232-ee9dc66cdc15
    msg_id = "2019-825aeb79-2681-4572-8232-ee9dc66cdc15"

    config = Config()
    api = PackitBotAPI(config)
    fedmsg_dict = api.consumerino.fetch_fedmsg_dict(msg_id)
    api.sync_upstream_release_with_fedmsg(fedmsg_dict)


def test_loop():
    pass
