# Optional Python File Exporter

Use this developer example when you need to save the page, checklist, and validation report automatically. For the basic Hermes-to-Scrapeless connection, start with the [integration README](../README.md).

## Quick start

### 0. Download the project and enter its directory

On this project's repository page, select **Code > Download ZIP**, extract it, and open the extracted project folder in your terminal. For the local review archive, extract `Scrapeless_Hermes_Web_Reader_Repo.zip`, then run:

```bash
cd scrapeless-hermes-web-reader
```

For a GitHub ZIP, replace the directory name with the actual extracted folder name, including any branch suffix. Confirm that `hermes_reader.py`, `requirements.txt`, and `config.json` are present. Run all subsequent commands from this directory.

### 1. Install and inspect an offline example

The exporter requires **Python 3.10+ with SQLite** and no third-party packages. Download the project, open its root in a terminal, then run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --no-index -r requirements.txt
python hermes_reader.py demo
```

For Windows, use `py -3 -m venv .venv` and `.venv\Scripts\Activate.ps1` in PowerShell. Live execution requires a Hermes-supported platform; the exporter running on Windows does not independently establish Hermes compatibility.

Open `output/demo/checklist.md`, `page.md` and `report.json`. This offline example contains selected original English output and source text from the retained October 29 run. It makes no new model or extraction request.

### 2. Prepare Hermes and configure the extraction tool

**Check the version first: this exporter supports Hermes v0.22.5 only.** This is an exporter restriction; follow the [integration guide](hermes.md) for ordinary MCP setup.

If Hermes is already installed, run `hermes --version`. Skip installation for v0.22.5. With another version, start with offline `demo` or use MCP through the integration guide; use a matching installation to reproduce file export.

For a fresh Linux, macOS, or WSL2 environment, the official installer can pin the commit behind v0.22.5. These commands install software; do not use them to overwrite an existing installation of another version:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh -o hermes-install.sh
bash hermes-install.sh --commit bf0203a794a07aac3ff764972ab9087baa4e4f4e
hermes --version
hermes model
hermes chat
```

The commit matches the [official v0.22.5 tag](https://github.com/NousResearch/hermes-agent/releases/tag/v0.22.5); `--commit` is supported by the [official installer source](https://github.com/NousResearch/hermes-agent/blob/main/scripts/install.sh). Confirm `hermes --version` reports v0.22.5 before continuing. Do not bypass the exporter version check.


After installation, reload your shell if the launcher is unavailable. `hermes model` opens provider selection: choose your provider, configure its own credential, and select a tool-capable model. Complete one normal chat so the active profile and session database exist. Model setup and a normal chat can use your provider's credits.

For a desktop installation, open **Models > Model Settings > Change** to review or select the model. Choose your own tool-capable model and provider in Hermes.


The model-provider key and the Scrapeless key are separate. Keep both in the active Hermes configuration, using the provider setup flow for the model key. Then confirm the launchers:


```bash
hermes --version
node --version
npx --version
```

The complete live run used **Hermes v0.22.5**, `scrapeless-mcp-server@0.6.3` and Python 3.12.14 for this exporter. Hermes manages its own separate Python runtime. The exporter currently accepts Hermes v0.22.5 only; other versions stop at preflight until their adapter is verified.

Use your existing key from **Settings > API Key Management** in the [Scrapeless dashboard](https://app.scrapeless.com/passport/login?redirect=%2Fquick-start&utm_source=github&utm_medium=referral&utm_campaign=scrapeless-hermes-web-reader&utm_content=repository-readme). Add this line to the active Hermes profile's `.env` file, normally `~/.hermes/.env`:

```dotenv
SCRAPELESS_API_KEY=YOUR_SCRAPELESS_API_KEY
```

The repository's `.env.example` is a reference. A repository-local `.env` is not loaded by this program. Keep model credentials in Hermes as well.

Merge the following into the active profile's `config.yaml`, normally `~/.hermes/config.yaml`. Preserve unrelated settings and other servers; update the existing `scrapeless` entry instead of duplicating it:

```yaml
# Merge this entry into the active Hermes profile; preserve other configuration.
mcp_servers:
  scrapeless:
    command: npx
    args: ["-y", "scrapeless-mcp-server@0.6.3"]
    env:
      SCRAPELESS_API_KEY: "${SCRAPELESS_API_KEY}"
    enabled: true
    tools:
      include: ["scrape_markdown"]
      resources: false
      prompts: false
```

Only the page-extraction tool is enabled for this example. Restart the conversation after configuration changes. If a background Gateway has stale environment values, restart it only when its running tasks have finished.

Check discovery without extracting a page:

```bash
hermes mcp list
hermes mcp test scrapeless
python hermes_reader.py check
```

`check` verifies the local Hermes version, required CLI options, the extraction-only tool selection and the session database schema. It makes no model or extraction request. Fix any failed check before `run`; a different version or schema stops before extraction. MCP discovery checks the connection. Confirm service access and credits separately.

### 3. Read the page and export the checklist

```bash
python hermes_reader.py run --output output/first-live
```

The default target is the official Hermes installation guide. Hermes is asked to extract it once, treat it as reference data, and list requirements with a source link. The exporter validates the completed call and the expected source text before saving:

```text
output/first-live/
  page.md
  checklist.md
  report.json
```

[![Actual checklist and report files exported during the complete live run](../assets/live-output-files.png)](../assets/live-output-files.png)

*Actual files from the complete October 29 live run, opened in a local file viewer. The checklist shows selected first items and the JSON shows selected report fields plus the measured command duration. One extraction produced 15,641 characters of source text and a 15-item checklist; the full exporter command took 28.82 seconds.*

## A real topic-to-checklist run

<table class="io-overview">
<thead><tr><th width="34%">INPUT: the topic</th><th width="66%">OUTPUT: the actual answer, selected commands</th></tr></thead>
<tbody><tr><td valign="top"><p><strong>Create and activate a Python virtual environment</strong></p><p>This is the exact text supplied with <code>--topic</code>.</p></td><td valign="top"><p><strong>1. Create the environment</strong><br><code>python -m venv /path/to/new/virtual/environment</code></p><p><strong>2. Activate on macOS/Linux (bash or zsh)</strong><br><code>source &lt;venv&gt;/bin/activate</code></p><p><strong>3. Activate on Windows PowerShell</strong><br><code>&lt;venv&gt;\Scripts\Activate.ps1</code></p><p><strong>4. Leave the environment</strong><br><code>deactivate</code></p></td></tr></tbody>
</table>

The full answer contains **7 setup steps, 15 checklist items and platform notes**. The commands above are selected unchanged from the [actual saved answer](../examples/topic-checklist-selection.md); they were returned as guidance. The source was the configured [official Python venv page](https://docs.python.org/3.12/library/venv.html).

### 1. Enter a topic and choose its source

The included [Python venv configuration](../examples/python-venv.json) points to the [official Python 3.12 documentation](https://docs.python.org/3.12/library/venv.html). `--topic` focuses the output on that subject within the specified source page.

After completing setup, run:

```bash
python hermes_reader.py check
python hermes_reader.py run --config examples/python-venv.json --topic "Create and activate a Python virtual environment" --output output/topic-python-venv --timeout 240
```

[![The exact user topic and source sent by the program, shown in the real Hermes session](../assets/topic-input.png)](../assets/topic-input.png)

*1: The topic entered through `--topic`. 2: The source URL loaded from the example configuration. Selected beginning of the actual program-generated prompt in Hermes History, captured October 29.*

### 2. Follow the actual extraction

Open the completed task in **Sessions > All > History** and expand `tool_call`:

[![Actual Scrapeless extraction call for the Python venv source](../assets/topic-tool-call.png)](../assets/topic-tool-call.png)

*1: The actual extraction tool. 2: The Python documentation URL. This run observed one extraction call, with no wrapper retry.*

### 3. Inspect the saved result

[![Actual topic-focused checklist, selected report fields and recorded program output](../assets/topic-results.png)](../assets/topic-results.png)

*Actual exported-file and execution-log viewer. The left pane preserves original setup steps 1, 4 and 5; the right pane shows selected unchanged report fields and a portable equivalent command and the program's actual exit output. Click to enlarge.*

| Measured result | Value |
| --- | --- |
| Extracted source | 34,742 characters |
| Generated guidance | 7 setup steps, 15 checklist items and platform notes |
| Complete program duration | 37.47 seconds |
| Saved files | `page.md`, `checklist.md`, `report.json` |

The answer includes environment creation, POSIX activation and Windows activation commands. The program extracted and organized the guidance; the generated setup commands were not executed. Review the commands for your platform before using them.

Open `output/topic-python-venv/checklist.md` for the complete answer and keep `page.md` beside it for verification. The [exact live report](../examples/topic-live-report.json) and [selected original output](../examples/topic-checklist-selection.md) are included in the repository. Use a new output directory when repeating the example.

## Configuration

| File / setting | Purpose |
| --- | --- |
| `--topic` / optional `topic` | Focus the answer on a subject within the supplied source; 1-200 characters on one line |
| `config.json` / `url` | Public HTTPS documentation URL; query strings and fragments are not accepted |
| `expected_text` | Case-sensitive phrases required in the extracted page |
| `mcp-config.yaml` | Mergeable Hermes configuration exposing only `scrape_markdown` |
| Hermes profile `.env` | Holds the existing Scrapeless key and model-provider configuration |
| `HERMES_HOME` | Optional active profile directory; the default session database follows it |

The default phrases are `Quick Install` and `Prerequisites`. When changing `--url`, the program clears the old target's expected phrases. Set new phrases in `config.json` for stronger content validation; a result without phrases is labeled `nonempty_text_only`.

## Usage

```bash
python hermes_reader.py demo --output output/another-demo
python hermes_reader.py run --url https://example.com --output output/example
python hermes_reader.py run --config config.json --timeout 240 --output output/custom
python hermes_reader.py run --hermes ~/.local/bin/hermes --output output/full-path
python hermes_reader.py --help
```

Run `python hermes_reader.py check` again after changing the Hermes version or configuration. A run requires a new or empty output directory. `--timeout` accepts 30-600 seconds, default 180. For a profile whose session database is elsewhere:

```bash
python hermes_reader.py run --state-db /path/to/active-profile/state.db --output output/profile-run
```

Use only pages you are authorized to retrieve. Basic checks reject embedded credentials, local literal addresses and query strings; they do not resolve DNS or implement a remote network access policy.

The wrapper launches Hermes without a shell, requests `mcp-scrapeless` and a four-iteration limit, and never retries automatically. Its validator rejects unexpected tools or multiple extractions **after execution**. This is an observed-call check, not a pre-execution spending cap; Hermes and its model provider manage their own internal behavior.

## Output

| File | Contents |
| --- | --- |
| `page.md` | Complete stored extraction for a live run; retained excerpt for the demo |
| `checklist.md` | The agent's sourced checklist; selected original English items for the demo |
| `report.json` | Mode, source, validation, content hash and provenance |

This selected demo report makes its origin explicit:

```json
{
  "mode": "offline_demo",
  "network_requests": 0,
  "original_observation_date": "2026-10-29",
  "validation": "bundled_example_only",
  "checklist_source": "Selected original English items from the retained answer"
}
```

A live report instead identifies `mode: "live"`, the actual UTC observation time, observed extraction count and validation level. Session identifiers and raw subprocess logs are omitted. Check the checklist against `page.md`; automated checks do not prove that every generated statement is correct.

## How it works

[![Public documentation passes through Hermes, Scrapeless MCP and the exporter to Markdown and JSON](../assets/workflow.png)](../assets/workflow.png)
1. Load and validate the target URL and expected phrases.
2. Ask the installed Hermes CLI to read the page using its configured Scrapeless MCP server.
3. Validate the JSON event stream, target URL, extraction count and final answer.
4. Read the new session's full tool result from Hermes `state.db` in read-only mode. This avoids the CLI stream's 5,000-character tool-preview limit.
5. Decode the provider response, check expected text, and write sanitized Markdown and JSON.

The session query uses the returned session ID and tool name, not the latest unrelated conversation. Preflight checks the supported v0.22.5 version, CLI and database columns before a new request. A concurrent or later schema change can still stop export; inspect the existing session before any deliberate repeat.

The new exporter completed a fresh live run on October 29: one extraction, 15,641 source characters, 15 numbered checklist items and all three output files. The full command took 28.82 seconds; this is the complete pipeline duration, not the tool-only latency. The [live report](../examples/live-report.json) and [actual checklist excerpt](../examples/live-checklist-excerpt.md) are included. The offline demo contains selected original English output from this run.

## Troubleshooting

| Symptom | Next step |
| --- | --- |
| `hermes` not found | Install Hermes or pass the full executable path with `--hermes` |
| MCP or key missing | Check the active profile, `.env` and server entry; restart the conversation |
| Credit or provider error | Stop and inspect service access/balance before any deliberate retry |
| Expected text missing | Check the actual target and markers; a nonempty error page is not success |
| Preflight version or schema error | Use the supported Hermes v0.22.5 and correct `--state-db`; update and verify the adapter before making another extraction |
| Timeout or interrupted result | The request may already have run; inspect Hermes History before starting again |
| Output directory not empty | Choose a fresh output directory |

## Development

```bash
python -m unittest discover -s tests -v
python hermes_reader.py demo --output output/test-demo
```

The 32 local tests cover preflight failures, wrong URLs, repeated/unexpected tools, transport/provider errors, source matching, full-result export, timeouts, redaction and existing-output protection. They make no model or Scrapeless requests. The same offline commands passed in a fresh Python 3.12.14 environment. GitHub Actions is supplied for Python 3.10 and 3.13; check the private draft repository for the current hosted CI result. See [CHANGELOG](../CHANGELOG.md) and the [MIT license](../LICENSE).

## Related projects

- [Scrapeless MCP Server](https://github.com/scrapeless-ai/scrapeless-mcp-server?utm_source=github&utm_medium=referral&utm_campaign=scrapeless-hermes-web-reader&utm_content=repository-readme) - The extraction tool connected to Hermes.
- [Scrapeless CLI](https://github.com/scrapeless-ai/scrapeless-cli?utm_source=github&utm_medium=referral&utm_campaign=scrapeless-hermes-web-reader&utm_content=repository-readme) - Use Scrapeless from your terminal.

## Learn more

- [Scrapeless MCP documentation](https://docs.scrapeless.com/en/docs/developer-tools/scrapeless-mcp/overview/?utm_source=github&utm_medium=referral&utm_campaign=scrapeless-hermes-web-reader&utm_content=repository-readme)
- [Hermes installation](https://hermes-agent.nousresearch.com/docs/getting-started/installation)
- [Hermes MCP configuration](https://hermes-agent.nousresearch.com/docs/reference/mcp-config-reference)

## Contact us

For this example, open an issue in the repository where it is hosted. Include your Python and Hermes versions, the command and a sanitized error. Never attach keys or private session databases.

For product help: [Discord](https://discord.gg/stFPK2xKHY?utm_source=github&utm_medium=referral&utm_campaign=scrapeless-hermes-web-reader&utm_content=repository-readme) or [Telegram](https://t.me/scrapeless?utm_source=github&utm_medium=referral&utm_campaign=scrapeless-hermes-web-reader&utm_content=repository-readme).
