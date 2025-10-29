# TNS E-messaging — Project Overview

## Purpose

TNS E-messaging is a small tooling project whose goal is to extract monthly billing/reading data from a specially-formatted Excel workbook, convert that data into a usable results file, generate personalized messages from templates, and deliver those messages over an SMS gateway.

## Quick user workflow

1. Place the prepared Excel workbook in `docs/source/`.
2. Ensure the environment has `API_KEY` and `DEVICE_ID` set (or a `.env` with those values).
3. Run the extractor to create/append the CSV for the billing month (the repository has `scripts/data_extraction.py`).
4. Generate messages from the CSV using the template filler (logic in `scripts/temp_filling.py`).
5. Send messages through the SMS gateway (the HTTP call is in `scripts/send_sms.py`).

## Files and roles (short)

- `scripts/data_extraction.py` — opens the Excel file, walks the fixed layout boxes, extracts customer rows, and calls CSV writer.
- `scripts/extracted_csv.py` — creates the monthly CSV and appends filtered rows.
- `scripts/temp_filling.py` — reads the CSV, maps columns to template variables, fills templates and returns message + contact.
- `scripts/send_sms.py` — sends a single message to the configured HTTP SMS gateway.
- `message_templates/` — templates for each location; keep templates clear and include the placeholders used by the filler.

## Usage notes and assumptions

- The extractor expects a fixed sheet name pattern and fixed box offsets. If your Excel layout changes, the extractor must be adapted.
- Contact normalization assumes local phone formatting and currently prepends a `+255` country code (see utilities). Update this if you target other countries.
- The CSV acts as the main persistence for extracted rows. There is no database or durable message queue yet.

## Limitations (what to expect right now)

- No delivery receipt tracking or message status storage. The system posts to the gateway but does not retain per-message delivery state.
- Minimal error handling and retries — network/API errors currently cause the process to exit.
- Single-threaded and synchronous: sending large batches will be slow.
- Templates use Python's basic string.format — missing fields or incorrect placeholders may raise exceptions.

## Recommendations — improvements to make this reliable and easy to use

1. Configuration and secrets

   - Move environment/config into a clear config file (YAML/JSON) or use a small CLI with flags. Provide an example `env.example` or `config.sample.yml`.
   - Use a secrets manager for API keys (or at minimum a `.env` that's excluded from git).

2. Robustness and error handling

   - Add structured logging (e.g., Python logging with rotating files). Log extraction counts, template failures, and API responses.
   - Implement network retries with exponential backoff for gateway calls and make send operations idempotent (track message IDs or use a message hash).
   - Validate template variables before substitution; when a placeholder is missing, write a clear diagnostic instead of raising.

3. Persistence and delivery tracking

   - Replace CSV-as-primary-storage with a small SQLite DB (or a lightweight key-value store). This allows recording per-message status (queued, sent, failed, delivered).
   - Store message request/response payloads and gateway message IDs for later correlation.

4. Batching, concurrency and rate control

   - Add a queuing layer (e.g., in-memory queue, Redis, or SQLite-backed job table) and a worker process to send messages.
   - Support configurable concurrency and rate limits to avoid exceeding gateway limits.

5. Testing and validation

   - Add unit tests for extraction logic (mock Excel cells) and template filling (various edge cases). Add small integration tests for CSV writing and template application.
   - Add a test runner and CI (GitHub Actions) that runs the tests and linting on push.

6. Operational / observability

   - Expose basic metrics (counts of extracted rows, messages sent, failures) and error alerts.
   - Save delivery receipts (if gateway supports) and show them in a simple UI or CSV export.

7. Usability improvements

   - Provide a small CLI wrapper (click/argparse) to run steps: extract, preview, queue, send, status.
   - Provide a `dry-run` mode that prints messages without sending.
   - Improve templates: consider using a safer templating engine (Jinja2) for clearer expressions and escaping.

8. Packaging and deployment
   - Containerize the app (Docker) so it runs reproducibly in environments and in scheduler/cron jobs.
   - Provide a `requirements.txt` pinfile and a short `docker-compose.yml` if you add a backing service like Redis.
