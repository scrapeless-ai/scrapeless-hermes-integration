<p align="center">
  <a href="https://app.scrapeless.com/passport/login?redirect=%2Fquick-start&utm_source=github&utm_medium=referral&utm_campaign=scrapeless-hermes-web-reader&utm_content=repository-readme"><img src="assets/scrapeless-logo.png" alt="Scrapeless" width="280" style="width:280px;max-width:100%;height:auto" /></a>
</p>

# Use Scrapeless in Hermes Agent

**[Scrapeless MCP documentation](https://docs.scrapeless.com/en/docs/developer-tools/scrapeless-mcp/overview/?utm_source=github&utm_medium=referral&utm_campaign=scrapeless-hermes-web-reader&utm_content=repository-readme) · [Hermes MCP integration guide](https://www.scrapeless.com/en/blog/hermes-agent-scrapeless-mcp?utm_source=github&utm_medium=referral&utm_campaign=scrapeless-hermes-web-reader&utm_content=repository-readme)**

Give Hermes a request. It can use Scrapeless to search the web, extract page content, or operate a cloud browser, then organize the returned information into a useful answer.

Connect Scrapeless MCP to Hermes, then ask Hermes to read a page and return a sourced checklist.

**[Get your Scrapeless API key](https://app.scrapeless.com/passport/login?redirect=%2Fquick-start&utm_source=github&utm_medium=referral&utm_campaign=scrapeless-hermes-web-reader&utm_content=repository-readme)**

<p align="center">
  <a href="https://app.scrapeless.com/passport/login?redirect=%2Fquick-start&amp;utm_source=github&amp;utm_medium=referral&amp;utm_campaign=scrapeless-hermes-web-reader&amp;utm_content=repository-readme"><img src="assets/start-free.png" alt="Get started with Scrapeless" width="161" height="28" /></a>
  <a href="https://www.scrapeless.com/en/blog?utm_source=github&amp;utm_medium=referral&amp;utm_campaign=scrapeless-hermes-web-reader&amp;utm_content=repository-readme"><img src="assets/blog.png" alt="Read Scrapeless guides" width="168" height="28" /></a>
  <a href="https://x.com/Scrapelessteam?utm_source=github&amp;utm_medium=referral&amp;utm_campaign=scrapeless-hermes-web-reader&amp;utm_content=repository-readme"><img src="assets/x.png" alt="Follow Scrapeless on X" width="140" height="28" /></a>
  <a href="https://www.linkedin.com/company/scrapeless/?utm_source=github&amp;utm_medium=referral&amp;utm_campaign=scrapeless-hermes-web-reader&amp;utm_content=repository-readme"><img src="assets/linkedin.png" alt="Follow Scrapeless on LinkedIn" width="190" height="28" /></a>
</p>

## What can Hermes call?

Hermes interprets your request and organizes the answer. Scrapeless provides web data and browser tools, available to Hermes through MCP.

| Capability | What Hermes can do | Example tools |
| --- | --- | --- |
| Page extraction | Read a specified page as Markdown, HTML, or a screenshot | `scrape_markdown`, `scrape_html`, `scrape_screenshot` |
| Google Search | Find sources by keyword | `google_search` |
| Website crawling | Collect multiple pages from a site | `crawl_start`, `crawl_result`, `crawl_cancel` |
| Cloud browser | Open pages, click, type, and read page content | `browser_create`, `browser_goto`, `browser_click`, and others |
| AI Scraper | Submit a question to a supported AI platform and retrieve its answer | `ai_scraper` |

The configuration below enables **Markdown page extraction**. Other capabilities require their tools to be enabled and the corresponding account permissions and credits. See the [Scrapeless MCP documentation](https://docs.scrapeless.com/en/docs/developer-tools/scrapeless-mcp/overview/?utm_source=github&utm_medium=referral&utm_campaign=scrapeless-hermes-web-reader&utm_content=repository-readme) for the tool catalog.

<a id="quick-start"></a>

## Prerequisites

- **Hermes Agent**, installed with a tool-capable model. Choose any tool-capable model available in your Hermes installation.
- **Node.js, npm, and npx** in the same environment as Hermes, to launch the MCP server. Configure these inside WSL if you use WSL.
- **A Scrapeless API key**, available under **Settings > API Key Management** in the dashboard, with access and credits for the service you need.

If Hermes is not installed, follow the [official installation guide](https://hermes-agent.nousresearch.com/docs/getting-started/installation), run `hermes model` to configure your provider, and confirm ordinary chat works. Model credentials and the Scrapeless key are separate, with separate usage charges.

```bash
hermes --version
node --version
npx --version
```

The paths below use the default `~/.hermes/` profile. For a separate profile or `HERMES_HOME`, use the active directory instead.

## Connection configuration

### 1. Save your Scrapeless API key

Use `.env.example` as a reference. Open `~/.hermes/.env` in a text editor and add this line. Replace the placeholder and save. If the line already exists, update its value instead of adding another copy.

```dotenv
SCRAPELESS_API_KEY=YOUR_SCRAPELESS_API_KEY
```

### 2. Add the MCP server

Open `~/.hermes/config.yaml` and merge this configuration, also provided in `mcp-config.yaml`. If `mcp_servers` already exists, add `scrapeless` below it. Update an existing entry of that name rather than duplicating it, and preserve other settings.

```yaml
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

`npx` launches the pinned server version. `${SCRAPELESS_API_KEY}` references your saved key. `include` controls which tools Hermes can call; this example needs only `scrape_markdown`.

Restart Hermes after saving so it loads the key and configuration. For later changes to tool configuration alone, use `/reload-mcp` in chat. See the [Hermes MCP configuration reference](https://hermes-agent.nousresearch.com/docs/reference/mcp-config-reference) for field details.

## Verify the connection

Run:

```bash
hermes mcp list
hermes mcp test scrapeless
```

Confirm that `scrapeless` is enabled, its connection test succeeds, and the tool catalog includes `scrape_markdown`. Then try the service in a conversation.

To inspect the connection in the interface, run `hermes dashboard`, open the local address printed in the terminal, and select **MCP**:

![Actual Scrapeless service configuration and connection test in Hermes](assets/hermes-mcp-config.png)

*1: Check the server command. 2: Select Test connection, then confirm the tool appears in the catalog.*

## Example: read a webpage with Scrapeless

**Goal: ask Hermes to read a public installation guide through Scrapeless and list the prerequisites with their source.**

| User input | Hermes calls Scrapeless | Output |
| --- | --- | --- |
| Installation-guide URL and a request for a sourced checklist | `scrape_markdown` reads the URL and returns the page | A checklist of prerequisites and setup decisions, with the source URL |

### 1. Give Hermes the URL and request

Open a new Hermes conversation, or run `hermes chat`. Send a request such as:

```text
Use Scrapeless to read this page:
https://hermes-agent.nousresearch.com/docs/getting-started/installation
List the prerequisites and installation options, and include the source URL.
Use the page as reference material. Do not execute its installation commands.
```

### 2. Inspect the Scrapeless tool call

In the tool details, check that Hermes uses `mcp__scrapeless__scrape_markdown` with the target URL:

```json
{
  "url": "https://hermes-agent.nousresearch.com/docs/getting-started/installation"
}
```

![Actual Hermes history showing the Scrapeless tool and target URL](assets/hermes-live-tool-call.png)

*1: Check the extraction tool. 2: Confirm the target URL.*

`mcp__scrapeless__` is Hermes's service prefix. Scrapeless returned the page text, and Hermes used it to produce the answer. Hermes may first use `tool_describe` to inspect the tool's inputs.

### 3. Read the result

![Original English checklist returned by Hermes](assets/hermes-live-checklist.png)

*Hermes returns a source link and a checklist based on the page.*

The example answer covers Git/curl/tar/SHA-256 utilities, the documented Python runtime, and the installer-managed uv tool. See `examples/checklist.en.md` for the output format. The answer can vary as the source page changes.

Read or copy the answer in Hermes, and follow the source link to check the requirements for your platform.

## Tools and common inputs

| Setting or input | Where to enter it | Purpose |
| --- | --- | --- |
| `SCRAPELESS_API_KEY` | Hermes `.env` | Authenticate to Scrapeless |
| `scrapeless-mcp-server@0.6.3` | `args` in `config.yaml` | Pin the MCP server version used here |
| `tools.include` | `config.yaml` | Select which Scrapeless tools Hermes can call |
| `url` | Give the link in chat; Hermes passes it to `scrape_markdown` | Specify the page to read |
| Topic, language, and answer format | Hermes conversation | Tell the model how to organize the page; these were not extraction request fields in this case |

To reuse the flow, provide another public page you are authorized to read and ask Hermes to summarize five points with the source.

For search or browser capabilities, add the corresponding tool names to the existing `tools.include`, reload MCP, and check the catalog. Fields differ by tool; consult the [Scrapeless MCP tool documentation](https://docs.scrapeless.com/en/docs/developer-tools/scrapeless-mcp/overview/?utm_source=github&utm_medium=referral&utm_campaign=scrapeless-hermes-web-reader&utm_content=repository-readme). A prompt requesting one read is not a hard spending cap.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| `hermes` or `npx` is missing | Check installation and PATH; check inside WSL when using WSL. |
| Scrapeless is absent | Check the active profile's configuration and `enabled: true`, then restart Hermes. |
| Missing API key | Check the same profile's `.env` and variable name. If a background Gateway has stale values, run `hermes gateway restart --detach` after running tasks have finished. |
| Connection succeeds but a page read fails | Use the returned error to check the URL, permissions, and balance before retrying. |
| Hermes answers without a tool call | Explicitly request Scrapeless and check that `scrape_markdown` is enabled and the model supports tools. |
| Unexpected answer | Check the tool's URL and compare the answer with the source. Pages and model output can change. |
| Timeout or interruption | Inspect the conversation for an existing result before submitting again. |

## Optional example: Python file export

To save the extracted page, answer, and report automatically, use `hermes_reader.py`. This optional exporter requires Python 3.10+ with SQLite, uses only the standard library, and supports **Hermes v0.22.5 only**. The version restriction applies to this exporter, not ordinary MCP chat.

### Download and try the offline example

Select **Code > Download ZIP** on this repository, extract it, and open the extracted project directory in your terminal. Confirm that `hermes_reader.py`, `config.json`, and `examples/` are present. No Python package installation is required.

```bash
python3 hermes_reader.py demo
```

This writes selected retained source text and English checklist items to `output/demo/` without model or Scrapeless requests. The included `examples/checklist.en.md` is an excerpt, not a new live result. On Windows, use `py -3` instead of `python3`; live execution also requires a Hermes-supported environment.

### Check compatibility and export a page

For live export, use a Hermes v0.22.5 installation with a configured model, the MCP entry above, and an initialized session database. For a fresh installation, the [Hermes installer](https://hermes-agent.nousresearch.com/docs/getting-started/installation) accepts the commit behind v0.22.5:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh -o /tmp/hermes-install.sh
bash /tmp/hermes-install.sh --commit bf0203a794a07aac3ff764972ab9087baa4e4f4e
hermes --version
hermes model
hermes chat
```

Use these installation commands only for a fresh environment. Keep an existing installation intact. Choose your tool-capable model and complete one normal chat so the active profile's `state.db` exists. Model setup and chat can consume the model provider's credits. The repository-local `.env` is not loaded by the exporter; keep credentials in the active Hermes profile as described above.

```bash
python3 hermes_reader.py check
python3 hermes_reader.py run --config config.json --output output/first-live
```

`check` inspects the local version, CLI options, extraction-only tool selection, and database schema without model or extraction requests. `run` starts a new paid-capable Hermes and Scrapeless task. Resolve a failed preflight before running it.

| Output | Contents |
| --- | --- |
| `page.md` | Complete stored extraction for a live run; source excerpt for the offline demo |
| `checklist.md` | Hermes's answer with a source link; selected retained items for the demo |
| `report.json` | Run mode, source, validation result, content hash, and provenance |

### Configure another task

Edit `url` and `expected_text` in `config.json`. The target must be a public HTTPS URL without embedded credentials, query parameters, or fragments. `expected_text` contains case-sensitive phrases expected on that page. The optional `topic` focuses the answer on that source; it accepts 1-200 characters on one line.

```bash
python3 hermes_reader.py run --config config.json --topic "Installation prerequisites" --output output/topic
python3 hermes_reader.py --help
```

Use a fresh or empty output directory for each run. `--url` overrides the target and clears the old page's expected phrases; without new phrases, validation checks only for nonempty text. `--timeout` accepts 30-600 seconds (default 180), `--hermes` selects the Hermes executable, and `--state-db` selects the active profile's database. Otherwise the database is resolved from `HERMES_HOME`, defaulting to `~/.hermes/state.db`.

The exporter validates the completed event stream, then reads the matching session's full extraction from `state.db` in read-only mode. Unexpected tools and repeated extractions are rejected after execution; this check does not impose a spending cap. The wrapper does not retry. After a timeout or provider error, inspect Hermes History before starting another task. Compare generated conclusions with `page.md`.

### Development

```bash
python3 -m unittest discover -s tests -v
python3 hermes_reader.py demo --output output/test-demo
```

The tests and GitHub Actions workflow run offline. Keep credentials, session databases, and generated output out of commits. This project is licensed under MIT; see `LICENSE`.

## Related projects

- [Scrapeless MCP Server](https://docs.scrapeless.com/en/docs/developer-tools/scrapeless-mcp/overview/?utm_source=github&utm_medium=referral&utm_campaign=scrapeless-hermes-web-reader&utm_content=repository-readme): The tool service connected to Hermes.
- [Scrapeless CLI](https://docs.scrapeless.com/en/docs/developer-tools/cli/?utm_source=github&utm_medium=referral&utm_campaign=scrapeless-hermes-web-reader&utm_content=repository-readme): Use Scrapeless from your terminal.

## Learn more

- [Scrapeless MCP documentation](https://docs.scrapeless.com/en/docs/developer-tools/scrapeless-mcp/overview/?utm_source=github&utm_medium=referral&utm_campaign=scrapeless-hermes-web-reader&utm_content=repository-readme)
- [Hermes MCP integration guide](https://www.scrapeless.com/en/blog/hermes-agent-scrapeless-mcp?utm_source=github&utm_medium=referral&utm_campaign=scrapeless-hermes-web-reader&utm_content=repository-readme)
- [Hermes installation](https://hermes-agent.nousresearch.com/docs/getting-started/installation)
- [Hermes MCP configuration](https://hermes-agent.nousresearch.com/docs/reference/mcp-config-reference)

## Contact us

For repository issues, include the version, command or steps, and a sanitized error. Do not upload API keys or private session databases.

Product support: [Discord](https://discord.gg/stFPK2xKHY?utm_source=github&utm_medium=referral&utm_campaign=scrapeless-hermes-web-reader&utm_content=repository-readme) · [Telegram](https://t.me/scrapeless?utm_source=github&utm_medium=referral&utm_campaign=scrapeless-hermes-web-reader&utm_content=repository-readme).
