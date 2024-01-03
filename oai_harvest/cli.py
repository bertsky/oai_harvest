import click
import uuid
import logging
import logging.config
from datetime import datetime
from oai_harvest.oai_harvest import harvest

logger = logging.getLogger(__name__)

@click.command(context_settings=dict(show_default=True))
@click.option(
    "--endpoint",
    help="endpoint of the OAI interface",
    required=True)
@click.option(
    "--ignore-deleted",
    help=("flag to wether ignore deleted records " +
          "(<header status=\"deleted\">)"),
    is_flag=True)
@click.option(
    "--encoding",
    help=("override the servers encoding, "),
    default="UTF-8")
@click.option(
    "--max-retries",
    help="number of retry attempts if an http request fails",
    default=5)
@click.option(
    "--metadata-prefix",
    help=("OAI PMH parameter 'metadataPrefix' " +
          "(http://www.openarchives.org/OAI/openarchivesprotocol.html#MetadataNamespaces), " +
          "i.e. metadata format"),
    default="dc")
@click.option(
    "--oai-set",
    help=("OAI PMH parameter 'set'" +
          "(http://www.openarchives.org/OAI/openarchivesprotocol.html#Set)"),
    required=True)
@click.option(
    "--harvest-from",
    metavar="DATE",
    help=("OAI PMH parameter 'from' " +
          "(http://www.openarchives.org/OAI/openarchivesprotocol.html#SelectiveHarvestingandDatestamps), " +
          "i.e. harvesting start"))
@click.option(
    "--harvest-until",
    metavar="DATE",
    help=("OAI PMH parameter 'until' " +
          "(http://www.openarchives.org/OAI/openarchivesprotocol.html#SelectiveHarvestingandDatestamps), " +
          "i.e. harvesting end"))
@click.option(
    "--date",
    metavar="DATE",
    help="ISO 8601 formatted date stamp",
    default=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))
@click.option(
    "--source-name",
    help="name to define the current harvesting source",
    default=str(uuid.uuid4())[:8])
@click.option(
    "--harvest-dir",
    metavar="PATH",
    help="path to the harvesting target dir",
    required=True)
@click.option(
    "--chunk-size",
    help="max number of records per chunk file",
    default=10000)
@click.option(
    "--chunk-node-name",
    help="name of the xml root node wrapping the records",
    default="Records")
@click.option(
    "--chunk-node-default-ns",
    help="default namespace of the chunk xml doc")
@click.option(
    "--chunk-node-ns",
    metavar="DICT",
    help=("additional namespace attributes of the " +
          "chunk xml doc the string json object"))
def cli(**kwargs):
    """
    ##### OAI harvest command line interface

    ###### installation:

    `python3 -m pip install git+https://git.slub-dresden.de/gersch/oai_harvest --user`

    ###### synopsis:

    `oai-harvest --help`

    \b
    `oai-harvest
        --endpoint 'https://base-oai.ubl-proxy.slub-dresden.de/oai'
        --oai-set 'collection:ftjcie AND autoclasscode:(302 OR 110)'
        --metadata-prefix base_dc
        --harvest-dir .`
    """
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}},
        "handlers": {
            "default": {
                "level": "INFO",
                "formatter": "standard",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr"}},
        "loggers": {
            "": {# root logger
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False}}}

    logging.config.dictConfig(logging_config)

    complete_list_size, record_total = harvest(**kwargs)
    assert complete_list_size == record_total, f"{complete_list_size} \u2260 {record_total}"

    logger.info(f"{complete_list_size} == {record_total}")
