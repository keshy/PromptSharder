### Map-reduce Design pattern for Prompt engineering

Project explores ability to model map-reduce jobs for offline prompt analysis on large documents.

#### Motivation

Given that prompt engineering provides the most flexible interface to reason and analyze data we seek to
evaluate the limits we can go to with this approach. Other approaches that are more favorable
for large amounts of data like Fine tuning, RAG etc have their own use cases
but its clear that those techniques require significant up front investment in getting variant training material
or be able to pre-materialize storage that's vectorized to be able to serve expected questions/requests.

We want to evaluate a method whereby we avoid both of those short comings at the cost of more inference calls and slower
analysis.
With a consistent increase across the board over time with token limits from leading models, we believe this is an
expected directions
the industry will gravitate wherein such frameworks and tooling would be required.

#### Competing frameworks

- Langchain has an offering/implementation which is more of a design pattern than a full blown end-to-end solution.

#### Solution highlights

- DSL/YAML based specification for engaging with the framework/service.
- Allows for configuration driven intermediate result filtering, reduction etc.
- Accounts for adaptive 'bin-packing' of document chunks to minimize required parallelism where possible and reduce API
  calls.
- Ensures low memory footprint irrespective of the size of the data. Uses chunked disk reads as opposed to pushing
  everything to memory.
- Provides completely pluggable architecture where you can bring your own OpenAI compliant language model.

#### How to run?

- ㊙ Create a secrets.yaml file that includes the required OpenAI environment variables stored under the `model_env_vars`
  key. E.g.

```
model_env_vars:
  AZURE_OPENAI_ENDPOINT: <Add your own>
  AZURE_OPENAI_API_KEY: <Add your own>
  OPENAI_API_TYPE: <Add your own>
  OPENAI_API_VERSION: <Add your own>
```

- ✅ Create a prompt_config.yaml file that includes required job specification. Below is a sample

```shell
---

prompt_template: |
  Provide the list of unique actors from analyzing the document below. Only character names would be good. Ignore any other text or numbers.
  
  #######
  {document}
map_reduce_method: parallel
max_token_limit: 4096
step_delay_in_seconds: 5
reducer_template: |
  Dedup all unique characters and provide a final list from the data provided below.
  
  ########
  {intermediate_results}
prompt_template_var: document
reducer_template_var: intermediate_results



```

- ⚙ run the job

```shell
(venv) (base) knarayan@M-XK0G99WFGM map_reduce_cli % python large_docs.py -h
usage: python3 large_docs.py --data <path to data folder> --config <path to config file> --secrets <path to secrets file>

CLI to enable large document processing with LLMs

options:
  -h, --help         show this help message and exit
  --data DATA        Path to the folder that needs to be processed
  --config CONFIG    Path to prompt_config.yml document that will guide how the file will be analyzed
  --secrets SECRETS  Path to secrets.yml document that will contain LLM model specs and credentials

 ```

- You can monitor intermediate job results in `/tmp/llm-mapreduce/` folder. Each job gets a folder with intermediate
  results and final results saved.

### 🚀 Roadmap

- Cross node scale out for parallelism and job management.
- Leverage external database for intermediate job management and results.
- Increase additional content type support - today only available for text files.
- Increase unit test coverage
- Address core component observability requirements.
- Add caching layers for commonly accessed chunks/results to optimize performance on repeated queries
- Develop UI components for making this a full blown application.
- Develop REST API endpoints for submitting jobs, monitoring status and retrieving results.
- Leverage more sophisticated job manager like Airflow for scheduling.

### ❗❗❗❗  Issues observed ❗❗❗❗❗

- Adding a sleep delay between the parallelism and intermediate jobs allow for more accuracy.
- Token math is complex. The same size of characters can have different token size depending on what's in the chunk.
  Using plain heuristics approach today for this but we could improve this in many ways. 