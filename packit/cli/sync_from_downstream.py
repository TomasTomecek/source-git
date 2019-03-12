"""
Update selected component from upstream in Fedora
"""

import logging
import os

import click

from packit.api import PackitAPI
from packit.cli.types import LocalProjectParameter
from packit.cli.utils import cover_packit_exception
from packit.config import pass_config, get_context_settings, get_local_package_config

logger = logging.getLogger(__file__)


@click.command("sync-upstream", context_settings=get_context_settings())
@click.option(
    "--dist-git-branch", help="Source branch in dist-git for sync.", default="master"
)
@click.option(
    "--dist-git-path",
    help="Path to dist-git repo to work in. "
    "Otherwise clone the repo in a temporary directory.",
)
@click.option(
    "--upstream-branch", help="Target branch in upstream to sync to.", default="master"
)
@click.option("--no-pr", is_flag=True, help="Pull request is not create.")
@click.argument(
    "repo", type=LocalProjectParameter(), default=os.path.abspath(os.path.curdir)
)
@pass_config
@cover_packit_exception
def sync_from_downstream(
    config, dist_git_path, dist_git_branch, upstream_branch, no_pr, repo
):
    """
    Sync downstream release into upstream

    REPO argument is a local path to the upstream git repository,
    it defaults to the current working directory
    """
    package_config = get_local_package_config(directory=repo.working_dir)
    package_config.downstream_project_url = dist_git_path
    package_config.upstream_project_url = repo.working_dir
    api = PackitAPI(config=config, package_config=package_config)
    api.sync_from_downstream(dist_git_branch, upstream_branch, no_pr)
