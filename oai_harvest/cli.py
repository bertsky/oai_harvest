import click
import uuid
import logging
import logging.config
from datetime import datetime
from oai_harvest.oai_harvest import harvest

logger = logging.getLogger(__name__)

@click.command()
@click.option(
    "--endpoint",
    help="endpoint of the oai interface",
    required=True)
@click.option(
    "--ignore-deleted",
    help=("flag to wether ignore deleted records " +
          "(<header status=\"deleted\">) or not"),
    is_flag=False)
@click.option(
    "--encoding",
    help=("override the servers encoding, " +
          "'request' will fallback to 'ISO-8859-1' default is 'UTF-8'"),
    default="UTF-8")
@click.option(
    "--max-retries",
    help="number of retry attempts if an http request fails (default is 5)",
    default=5)
@click.option(
    "--metadata-prefix",
    help=("oai pmh parameter metadata prefix (default is 'dc') " +
          "'http://www.openarchives.org/OAI/openarchivesprotocol.html#MetadataNamespaces'"),
    default="dc")
@click.option(
    "--oai-set",
    help=("oai pmh parameter set" +
          "'http://www.openarchives.org/OAI/openarchivesprotocol.html#Set'"),
    required=True)
@click.option(
    "--harvest-from",
    help=("oai pmh parameter from, harvesting start datestamp " +
          "'http://www.openarchives.org/OAI/openarchivesprotocol.html#SelectiveHarvestingandDatestamps'"))
@click.option(
    "--harvest-until",
    help=("oai pmh parameter until, harvesting end datestamp " +
          "'http://www.openarchives.org/OAI/openarchivesprotocol.html#SelectiveHarvestingandDatestamps'"))
@click.option(
    "--date",
    help="default is current date ('%Y-%m-%dT%H:%M:%SZ')",
    default=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))
@click.option(
    "--source-name",
    help="name to define the current harvesting source (default uuid)",
    default=str(uuid.uuid4())[:8])
@click.option(
    "--harvest-dir",
    help="path to the harvesting target dir",
    required=True)
@click.option(
    "--chunk-size",
    help="max number of records per chunk file (default 10.000)",
    default=10000)
@click.option(
    "--chunk-node-name",
    help="name of the xml root node wrapping the records",
    default="Records")
@click.option(
    "--chunk-node-default-ns",
    help="default namespace of the chunk xml doc")
@click.option(
    "-chunk-node-ns",
    help=("additional namespace attributes of the " +
          "chunk xml doc the string json object"))
def cli(
    endpoint="https://base-oai.ubl-proxy.slub-dresden.de/oai",
    ignore_deleted=False,
    encoding="UTF-8",
    max_retries=5,
    metadata_prefix="base_dc",
    oai_set="collection:ftjcie AND autoclasscode:(302 OR 110)",
    harvest_from=None,
    harvest_until=None,
    date=None,
    source_name=None,
    harvest_dir="./_resources",
    chunk_size=1,
    chunk_node_name="Records",
    chunk_node_default_ns=None,
    chunk_node_ns=None):
    """
    ##### oai harvest command line interface

    ###### installation:

    `python3 -m pip install git+https://git.slub-dresden.de/gersch/oai_harvest --user`

    ###### synopsis:

    `oai-harvest --help`

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

    complete_list_size, record_total = harvest(
        endpoint=endpoint,
        ignore_deleted=ignore_deleted,
        encoding=encoding,
        max_retries=max_retries,
        metadata_prefix=metadata_prefix,
        oai_set=oai_set,
        harvest_from=harvest_from,
        harvest_until=harvest_until,
        chunk_size=chunk_size,
        chunk_node_name=chunk_node_name,
        chunk_node_default_ns=chunk_node_default_ns,
        chunk_node_ns=chunk_node_ns,
        date=date,
        source_name=source_name,
        harvest_dir=harvest_dir)

    assert complete_list_size == record_total, f"{complete_list_size} \u2260 {record_total}"

    logger.info(f"{complete_list_size} == {record_total}")
