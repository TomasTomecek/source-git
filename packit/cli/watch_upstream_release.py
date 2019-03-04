#!/usr/bin/python3
"""
Watch for new upstream releases.
"""
import logging

import click

from packit.bot_api import PackitBotAPI
from packit.config import pass_config
from packit.constants import URM_CHOICE, GH2FEDMSG

logger = logging.getLogger(__name__)


@click.command("watch-releases")
@click.option(
    "--event-source",
    help=(
        "Source of events: either Upstream release monitoring (URM) or github2fedmsg. "
        "Please don't change this if you don't understand the option."
    ),
    default=URM_CHOICE,
    type=click.Choice([URM_CHOICE, GH2FEDMSG])
)
@click.argument("message-id", nargs=-1)
@pass_config
def watch_releases(config, message_id, event_source):
    """
    watch for activity on github and create a downstream PR

    :return: int, retcode
    """
    api = PackitBotAPI(config)
    if message_id:
        for msg_id in message_id:
            fedmsg_dict = api.consumerino.fetch_fedmsg_dict(msg_id)
            api.sync_upstream_release_with_fedmsg(fedmsg_dict)
    else:
        if event_source == GH2FEDMSG:
            api.sync_upstream_releases_using_gh2fed()
        elif event_source == URM_CHOICE:
            api.sync_upstream_releases_using_urm()
        else:
            logger.error("This should not have happened, we owe you a beer.")
