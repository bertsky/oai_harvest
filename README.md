<a id="oai_harvest.cli.cli"></a>

#### cli

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

<a id="oai_harvest.oai_harvest.harvest"></a>

#### harvest

simple oai harvesting module
utilizing [sickle](https://github.com/mloesch/sickle)

**Arguments**:

- `endpoint` _str, required_ - Endpoint of the oai interface. Defaults to None.
- `ignore_deleted` _bool, optional_ - Flag to wether ignore deleted records '(\<header status="deleted"\>)' or not. Defaults to False.
- `encoding` _str, optional_ - Override the servers encoding, request will fallback to 'ISO-8859-1'. Defaults to "UTF-8".
- `max_retries` _int, optional_ - Number of retry attempts if an http request fails. Defaults to 5.
- `metadata_prefix` _str, optional_ - OAI pmh parameter metadata prefix ('http://www.openarchives.org/OAI/openarchivesprotocol.html#MetadataNamespaces'). Defaults to "dc".
- `oai_set` _str, required_ - OAI pmh parameter set ('http://www.openarchives.org/OAI/openarchivesprotocol.html#Set'). Defaults to None.
- `harvest_from` _str, optional_ - OAI pmh parameter 'from', harvesting start datestamp ('http://www.openarchives.org/OAI/openarchivesprotocol.html#SelectiveHarvestingandDatestamps'). Defaults to None.
- `harvest_until` _str, optional_ - OAI pmh parameter 'until', harvesting end datestamp ('http://www.openarchives.org/OAI/openarchivesprotocol.html#SelectiveHarvestingandDatestamps'). Defaults to None.
- `date` _str, optional_ - Current date ('%Y-%m-%dT%H:%M:%SZ'). Defaults to None.
- `source_name` _str, optional_ - Name to define the current harvesting source. Defaults to None.
- `harvest_dir` _str, optional_ - Path to the harvesting target dir. Defaults to None.
- `chunk_size` _int, optional_ - Max number of records per chunk file. Defaults to 10000.
- `chunk_node_name` _str, optional_ - Name of the xml root node wrapping the records. Defaults to None.
- `chunk_node_default_ns` _str, optional_ - Default namespace of the chunk xml doc. Defaults to None.
- `chunk_node_ns` _str, optional_ - Additional namespace attributes of the chunk xml doc the string json object. Defaults to None.


**Returns**:

- `tuple` - number of records related to the current ListRecords - request (target record num) and number of records written to all chunk files (actual record num).

