import uuid
import pathlib
import logging
import logging.config
import click
import json
from base64 import urlsafe_b64encode
from sickle import Sickle
from datetime import datetime
from lxml import etree as ET

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

logger = logging.getLogger(__name__)

def _prep_chunk(
    chunk,
    chunk_num,
    harvest_dir,
    source_name,
    date,
    oai_set,
    ignore_deleted,
    chunk_node_name,
    chunk_node_default_ns,
    chunk_node_ns):
    """prep chunk doc xml and related chunk file"""
    save_set = ""
    if oai_set:
        save_set = f"_{urlsafe_b64encode(oai_set.encode('UTF-8')).decode('UTF-8').replace('=', '-')}"

    chunk_file_name = str(pathlib.Path(
        harvest_dir,
        f"{chunk_num}_{source_name}{save_set}_{date}.xml"))

    records = []
    for rec in chunk:
        if ignore_deleted and rec.header.deleted:
            next
        else:
            records.append(rec)

    if records:
        try:
            pathlib.Path(harvest_dir).mkdir(parents=True)
        except FileExistsError:
            pass

        try:
            pathlib.Path(chunk_file_name).touch()
        except FileExistsError:
            pass

        ns_map = {}
        if chunk_node_ns is not None:
            json_obj = None
            try:
                json_obj = json.loads(chunk_node_ns)
            except json.decoder.JSONDecodeError:
                pass

            if json_obj is not None:
                ns_map = json_obj

        if chunk_node_default_ns is not None:
                ns_map.update({None: chunk_node_default_ns})

        with ET.xmlfile(chunk_file_name, encoding="UTF-8") as xf:
            xf.write_declaration()
            with xf.element(chunk_node_name, nsmap=ns_map):
                for rec in records:
                    xf.write(rec.xml)

        logger.info(f"wrote {len(chunk)} records to {chunk_file_name}")
    else:
        logger.info(f"no records available to write to chunk file, "
                    f"skip writing {chunk_file_name}")

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
def harvest(
    endpoint=None,
    ignore_deleted=False,
    encoding="UTF-8",
    max_retries=5,
    metadata_prefix="dc",
    oai_set=None,
    harvest_from=None,
    harvest_until=None,
    date=None,
    source_name=None,
    harvest_dir=None,
    chunk_size=10000,
    chunk_node_name=None,
    chunk_node_default_ns=None,
    chunk_node_ns=None):
    """simple oai harvesting module
    utilizing [sickle](https://github.com/mloesch/sickle)

    command line usage: `oai-harvest --help`

    Args:
        endpoint (str, required): Endpoint of the oai interface. Defaults to None.
        ignore_deleted (bool, optional): Flag to wether ignore deleted records '(\<header status="deleted"\>)' or not. Defaults to False.
        encoding (str, optional): Override the servers encoding, request will fallback to 'ISO-8859-1'. Defaults to "UTF-8".
        max_retries (int, optional): Number of retry attempts if an http request fails. Defaults to 5.
        metadata_prefix (str, optional): OAI pmh parameter metadata prefix ('http://www.openarchives.org/OAI/openarchivesprotocol.html#MetadataNamespaces'). Defaults to "dc".
        oai_set (str, required): OAI pmh parameter set ('http://www.openarchives.org/OAI/openarchivesprotocol.html#Set'). Defaults to None.
        harvest_from (str, optional): OAI pmh parameter 'from', harvesting start datestamp ('http://www.openarchives.org/OAI/openarchivesprotocol.html#SelectiveHarvestingandDatestamps'). Defaults to None.
        harvest_until (str, optional): OAI pmh parameter 'until', harvesting end datestamp ('http://www.openarchives.org/OAI/openarchivesprotocol.html#SelectiveHarvestingandDatestamps'). Defaults to None.
        date (str, optional): Current date ('%Y-%m-%dT%H:%M:%SZ'). Defaults to None.
        source_name (str, optional): Name to define the current harvesting source. Defaults to None.
        harvest_dir (str, optional): Path to the harvesting target dir. Defaults to None.
        chunk_size (int, optional): Max number of records per chunk file. Defaults to 10000.
        chunk_node_name (str, optional): Name of the xml root node wrapping the records. Defaults to None.
        chunk_node_default_ns (str, optional): Default namespace of the chunk xml doc. Defaults to None.
        chunk_node_ns (str, optional): Additional namespace attributes of the chunk xml doc the string json object. Defaults to None.

    Returns:
        tuple: number of records related to the current ListRecords - request (target record num) and number of records written to all chunk files (actual record num).
    """
    sickle = None
    if endpoint is not None and oai_set is not None:
        sickle = Sickle(**{
            "endpoint": endpoint,
            "encoding": encoding,
            "max_retries": max_retries})
    else:
        raise Exception("missing required arguments 'endpoint' and 'oai_set'")

    if sickle is not None:
        records = None

        list_records_args = {"metadataPrefix": metadata_prefix}
        if oai_set is not None:
            list_records_args["set"] = oai_set
        if harvest_from is not None:
            list_records_args["from"] = harvest_from
        if harvest_until is not None:
            list_records_args["until"] = harvest_until

        logger.info(f"oai harvesting list records args: {list_records_args}")

        records = sickle.ListRecords(**list_records_args)

        complete_list_size = None
        if (records.resumption_token is not None and
            records.resumption_token.complete_list_size is not None):
                complete_list_size = int(
                    records.resumption_token.complete_list_size)

        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        chunk = set()

        prep_chunk_args = {
            "chunk": chunk,
            "chunk_num": 0,
            "oai_set": oai_set,
            "chunk_node_name": chunk_node_name,
            "chunk_node_default_ns": chunk_node_default_ns,
            "chunk_node_ns": chunk_node_ns,
            "ignore_deleted": ignore_deleted,
            "harvest_dir": harvest_dir,
            "source_name": source_name,
            "date": date}

        if date is None:
            prep_chunk_args["date"] = now
        if ignore_deleted is None:
            prep_chunk_args["ignore_deleted"] = False
        if source_name is None:
            prep_chunk_args["source_name"] = str(uuid.uuid4())[:8]
        if harvest_dir is None:
            prep_chunk_args["harvest_dir"] = f"./oai_harvest_{now}"
        if chunk_node_name is None:
            prep_chunk_args["chunk_node_name"] = "Records"

        record_total = 0

        for r in records:
            if len(chunk) == chunk_size:
                _prep_chunk(**prep_chunk_args)
                record_total += len(chunk)
                chunk = set()
                prep_chunk_args["chunk_num"] = prep_chunk_args["chunk_num"]+1

            chunk.add(r)

        if chunk:
            _prep_chunk(**prep_chunk_args)
            record_total += len(chunk)

        if complete_list_size is None:
            complete_list_size = record_total

        return complete_list_size, record_total
