# Home Assistant Integration Quality Scale — Universal Checklist

> Source (overview): https://developers.home-assistant.io/docs/core/integration-quality-scale/
> Source (rules index): https://developers.home-assistant.io/docs/core/integration-quality-scale/checklist
> Per-rule pages: `https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/<rule-id>`
> Fetched: 2026-04-14

## How to use

- **Self-audit workflow.** Start at Bronze and walk every rule top-to-bottom. For each rule, check the "Verify by" line and look for the concrete artifact (file, attribute, test, or documentation section) in your integration. Do not mark a rule satisfied unless the artifact actually exists — missing tests or missing docs are the most common silent failures.
- **Tiers cascade.** To reach a tier, the integration must fulfill **all rules of that tier and every lower tier** (Silver = Bronze + Silver rules, Gold = Bronze + Silver + Gold rules, Platinum = everything).
- **Declaring the tier.** The achieved tier is declared in `manifest.json` via the `quality_scale` key, e.g. `"quality_scale": "silver"`. Core integrations also track rule-by-rule progress in a per-integration `quality_scale.yaml` that lists each rule with `status: done | todo | exempt` plus an optional reason.
- **Exemptions are explicit.** If a rule genuinely does not apply (for example `action-setup` when no service actions are registered), mark it `exempt` with a one-line reason rather than silently skipping it.
- **Use the flat appendix as a PR / issue template.** Copy the Appendix block into a checklist when proposing a tier bump.

## Tier Summary

| Tier     | Purpose                                                                                                        | New rules | Cumulative |
|----------|----------------------------------------------------------------------------------------------------------------|-----------|------------|
| No scale | Not yet scored or lacking sufficient information for scoring. May function but is unverified.                  | 0         | 0          |
| Bronze   | Baseline for new integrations. Minimum code quality, functionality, and UX.                                    | 18        | 18         |
| Silver   | Reliability and robustness: active owner, error handling, automatic recovery, detailed docs.                   | 10        | 28         |
| Gold     | Gold-standard UX: discovery, full translations, devices lifecycle, comprehensive docs, full test coverage.     | 21        | 49         |
| Platinum | Technical excellence: fully typed, fully async, efficient session handling.                                    | 3         | 52         |

Total: **52 rules** (cumulative — Platinum means all 52 rules satisfied).

---

## Bronze — 18 rules

### [ ] action-setup — Service actions are registered in async_setup
**Requires:** All service actions (`hass.services.async_register(...)`) are registered in the integration's `async_setup` function, not in `async_setup_entry`. This keeps actions available even when no config entry is loaded.
**Verify by:** Grep for `async_register` and confirm every call sits inside `async def async_setup(hass, config)` in `__init__.py`, not inside `async_setup_entry`. If the integration has no services, mark **exempt**.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/action-setup

### [ ] appropriate-polling — Appropriate polling interval
**Requires:** Polling integrations set a sensible `update_interval` on the `DataUpdateCoordinator` (or `SCAN_INTERVAL` for legacy patterns). The interval must match how fast the upstream data actually changes — never poll faster than the source updates.
**Verify by:** Find the coordinator instantiation and inspect `update_interval=timedelta(...)`. Confirm the value is justified in docs or a comment (e.g. "device pushes to cloud every 60 s"). Push-only integrations mark **exempt**.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/appropriate-polling

### [ ] brands — Branding assets submitted
**Requires:** The integration has an icon (and optionally a logo) submitted to the [home-assistant/brands](https://github.com/home-assistant/brands) repository. The icon must be square PNG at 256×256 and 512×512.
**Verify by:** Check that `https://brands.home-assistant.io/<domain>/icon.png` returns a valid image. For custom components, acceptance into `home-assistant/brands` is the definitive artifact.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/brands

### [ ] common-modules — Common patterns in common modules
**Requires:** Recurring patterns (coordinator, entity base classes) live in dedicated modules — typically `coordinator.py` for the `DataUpdateCoordinator` subclass and `entity.py` for the shared entity base class. Platforms (`sensor.py`, `binary_sensor.py`, …) import from these, not the other way around.
**Verify by:** Confirm `coordinator.py` and `entity.py` exist. Check that platform files import the base entity from `.entity` and the coordinator from `.coordinator`.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/common-modules

### [ ] config-flow-test-coverage — Full test coverage for the config flow
**Requires:** The config flow has **100%** test coverage. Every step, every error path (auth errors, connection errors, duplicate detection), and every reauth/reconfigure branch is covered.
**Verify by:** Run `pytest --cov=custom_components.<domain>.config_flow --cov-report=term-missing` (or the core equivalent). Expect `100%` on that module.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/config-flow-test-coverage

### [ ] config-flow — UI-based setup
**Requires:** `"config_flow": true` in `manifest.json` and a working `config_flow.py` with a `ConfigFlow` subclass. YAML configuration is not allowed for new integrations. Where possible, user-facing fields use `selector` helpers with `section`s for grouping and store non-connection settings under the config entry's `options`.
**Verify by:** `manifest.json` has `"config_flow": true`; `config_flow.py` exists and implements `async_step_user`. Try adding the integration via **Settings → Devices & Services → Add Integration**.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/config-flow

### [ ] dependency-transparency — Dependency transparency
**Requires:** Every third-party package listed under `manifest.json["requirements"]` must be (a) published to PyPI by an identifiable maintainer, (b) open-source, and (c) built in a reproducible way. No wheels from private indexes, no obfuscated packages.
**Verify by:** For each entry in `requirements`, confirm it resolves on `pypi.org` with a visible source repository. No-requirement integrations mark **exempt**.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/dependency-transparency

### [ ] docs-actions — Documentation describes provided service actions
**Requires:** Every service action registered by the integration is described in user-facing documentation, with inputs, outputs, and an example.
**Verify by:** Open the integration's docs page (or README for custom components) and confirm a **Services** / **Actions** section lists each service by name. No-services integrations mark **exempt**.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/docs-actions

### [ ] docs-high-level-description — High-level description in docs
**Requires:** Documentation opens with a clear, high-level description: what the integration does, what vendor/service it talks to, and what the user gains by installing it.
**Verify by:** Read the first paragraph of the docs. A new user should understand the integration's purpose without jargon or scrolling.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/docs-high-level-description

### [ ] docs-installation-instructions — Step-by-step installation instructions
**Requires:** Docs list concrete setup steps: add integration, enter credentials, any account-side prerequisites (API keys, 2FA requirements, hardware pairing).
**Verify by:** Check for a `## Configuration` or `## Setup` section with numbered steps. Prerequisites that aren't obvious from the UI (e.g. "disable 2FA", "set unit to Celsius") must be called out explicitly.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/docs-installation-instructions

### [ ] docs-removal-instructions — Removal instructions
**Requires:** Docs explain how to cleanly remove the integration, including any vendor-side cleanup (revoking tokens, deleting the account's cloud binding).
**Verify by:** Check for a `## Removal` / `## Uninstall` section. Verify it covers both HA-side deletion and vendor-side cleanup where relevant.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/docs-removal-instructions

### [ ] entity-event-setup — Entity events subscribed in correct lifecycle
**Requires:** Event subscriptions (to a library, bus, or websocket) happen in `async_added_to_hass` and are torn down in `async_will_remove_from_hass`. Never subscribe in `__init__`.
**Verify by:** Grep for `async_added_to_hass` / `async_will_remove_from_hass` in entity classes. Confirm every `.subscribe()` / `.add_listener()` call lives inside the lifecycle method and has a matching unsubscribe returned via `self.async_on_remove(...)`.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-event-setup

### [ ] entity-unique-id — Entities have unique IDs
**Requires:** Every entity provides a stable, device-specific `unique_id`. The ID must survive HA restarts, network moves, and renames. Prefer hardware identifiers (serial, MAC) over anything the user can change.
**Verify by:** Grep for `_attr_unique_id = ` and confirm it is composed from stable device identifiers (e.g. `f"{device_sn}_{key}"`). Never use `self.name` or the user-provided label.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-unique-id

### [ ] has-entity-name — Entities use `has_entity_name = True`
**Requires:** Entities set `_attr_has_entity_name = True` and use translated entity names via `translation_key` (or device-class-only entities that inherit the class name).
**Verify by:** Grep for `_attr_has_entity_name` in every entity class. Confirm `_attr_translation_key` is set and matched by a key under `entity.<platform>.<key>.name` in `strings.json` / `translations/en.json`.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/has-entity-name

### [ ] runtime-data — Use `ConfigEntry.runtime_data`
**Requires:** Per-entry runtime state (coordinator, API client, session) is stored on `entry.runtime_data`, not on `hass.data[DOMAIN][entry.entry_id]`. The config entry type is aliased (e.g. `type MyConfigEntry = ConfigEntry[MyRuntimeData]`).
**Verify by:** Grep for `entry.runtime_data =` in `async_setup_entry`. There should be zero writes to `hass.data[DOMAIN]` for per-entry state (globals registered during `async_setup` are fine).
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/runtime-data

### [ ] test-before-configure — Test connection in the config flow
**Requires:** `async_step_user` actually attempts a connection / login before creating the entry, and returns the appropriate error (`cannot_connect`, `invalid_auth`) on failure.
**Verify by:** Read `async_step_user`. Confirm it calls the API client's login/ping method and maps specific exceptions to specific error codes. A test should assert `errors={"base": "cannot_connect"}` when the client raises a connection error.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/test-before-configure

### [ ] test-before-setup — Verify setup is possible on init
**Requires:** `async_setup_entry` raises `ConfigEntryNotReady` on transient failures (network, timeouts) and `ConfigEntryAuthFailed` on permanent auth failures. HA handles retry/reauth automatically from there.
**Verify by:** Grep `async_setup_entry` for raises of `ConfigEntryNotReady` and `ConfigEntryAuthFailed`. Initial coordinator refresh (`await coordinator.async_config_entry_first_refresh()`) naturally surfaces these when mapped properly in `_async_update_data`.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/test-before-setup

### [ ] unique-config-entry — Prevent duplicate entries
**Requires:** The config flow aborts with `already_configured` when the user tries to add the same account/device twice. Achieved via `await self.async_set_unique_id(...)` + `self._abort_if_unique_id_configured()`.
**Verify by:** Grep `config_flow.py` for `async_set_unique_id` followed by `_abort_if_unique_id_configured`. Add a test that runs the flow twice with the same credentials and asserts the second attempt aborts.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/unique-config-entry

---

## Silver — 10 rules (additional, on top of Bronze)

### [ ] action-exceptions — Service actions raise on failure
**Requires:** Service action handlers raise `HomeAssistantError` (or `ServiceValidationError` for bad input) on failure, rather than silently logging. Errors surface to the user in the UI.
**Verify by:** Grep service handlers (`async def async_handle_<service>`) for `raise HomeAssistantError(...)`. Silent `_LOGGER.error` without `raise` fails this rule. Exempt if no services.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/action-exceptions

### [ ] config-entry-unloading — Supports config entry unloading
**Requires:** `async_unload_entry` is implemented and cleanly tears down all resources (listeners, sessions, subscribers). After unload, nothing from the old entry keeps running.
**Verify by:** Open `__init__.py` for `async def async_unload_entry`. Confirm it calls `hass.config_entries.async_unload_platforms` and unregisters any bus listeners created during setup. Test: add, then remove the entry — the next `async_setup_entry` should succeed without restart.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/config-entry-unloading

### [ ] docs-configuration-parameters — Document all config options
**Requires:** Every field exposed in the **Options flow** is documented (name, type, range, default, effect).
**Verify by:** Cross-reference `async_step_init` of the options flow against a `## Options` / `## Configuration` section in docs. Every schema key must appear. Exempt if the integration has no options flow.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/docs-configuration-parameters

### [ ] docs-installation-parameters — Document installation parameters
**Requires:** Every field shown during initial setup (user step, discovery step) is documented — what to enter, where to get it, format constraints.
**Verify by:** Each key in the user-step schema (e.g. `CONF_EMAIL`, `CONF_PASSWORD`, `CONF_HOST`) is explained in docs, including where the user obtains the value.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/docs-installation-parameters

### [ ] entity-unavailable — Mark entities unavailable when appropriate
**Requires:** Entities return `available = False` when the underlying device/service is unreachable. The coordinator's `last_update_success` is the normal signal — inherit `CoordinatorEntity` and let it handle availability, or override `available` explicitly.
**Verify by:** Grep for `CoordinatorEntity` (auto-handles availability) or a custom `@property def available(self)`. Pull the network plug and confirm entities show as "Unavailable" in the UI, not stale values.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-unavailable

### [ ] integration-owner — Integration has an owner
**Requires:** `manifest.json["codeowners"]` lists at least one GitHub handle. The owner is responsible for reviewing PRs and responding to issues.
**Verify by:** Check `manifest.json` for `"codeowners": ["@handle"]`. Empty list fails.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/integration-owner

### [ ] log-when-unavailable — Log once on down, once on recovery
**Requires:** When the device/service goes unreachable, log a single warning. When it comes back, log a single info message. Do **not** spam logs on every failed poll. The `DataUpdateCoordinator` handles this automatically when `_async_update_data` raises `UpdateFailed`.
**Verify by:** Read `_async_update_data`. Confirm transient failures raise `UpdateFailed` (so the coordinator deduplicates warnings) rather than logging inside the method. Simulate an outage and verify the log has exactly one "unavailable" and one "available again" message.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/log-when-unavailable

### [ ] parallel-updates — `PARALLEL_UPDATES` declared
**Requires:** Each platform file declares `PARALLEL_UPDATES = <int>` at module level. Zero means unlimited; any positive number throttles concurrent `async_update` calls. Coordinator-based integrations typically use `PARALLEL_UPDATES = 0`.
**Verify by:** Grep each platform file (`sensor.py`, `binary_sensor.py`, …) for `PARALLEL_UPDATES =`. Missing declaration fails.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/parallel-updates

### [ ] reauthentication-flow — Reauth available in the UI
**Requires:** The config flow implements `async_step_reauth` + `async_step_reauth_confirm`. When auth expires or the password changes, raising `ConfigEntryAuthFailed` from `async_setup_entry` or `_async_update_data` triggers a repair notification that walks the user through re-auth without deleting the entry.
**Verify by:** Grep for `async_step_reauth_confirm` in `config_flow.py`. Verify that the coordinator raises `ConfigEntryAuthFailed` on 401/403, not `UpdateFailed`.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/reauthentication-flow

### [ ] test-coverage — Above 95% test coverage
**Requires:** All integration modules (not just the config flow) have **>95%** test coverage. Typically measured via `pytest --cov=custom_components.<domain>`.
**Verify by:** Run the coverage tool and confirm every module reports >95%. A single untested helper file can drop the aggregate below the threshold.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/test-coverage

---

## Gold — 21 rules (additional, on top of Silver)

### [ ] devices — Integration creates devices
**Requires:** Entities are attached to `DeviceInfo` so they group under a single device in the UI (manufacturer, model, sw_version, identifiers). One physical device → one HA device.
**Verify by:** Grep entity classes for `_attr_device_info = DeviceInfo(...)` or a `device_info` property. Identifiers must be stable (`(DOMAIN, serial_number)`), not the entry ID.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/devices

### [ ] diagnostics — Implements diagnostics
**Requires:** `diagnostics.py` exports `async_get_config_entry_diagnostics` (and optionally `async_get_device_diagnostics`). All secrets (passwords, tokens, PII) are redacted via `async_redact_data`.
**Verify by:** Check for `diagnostics.py`. Trigger **Download diagnostics** from the UI and confirm the output contains useful state but zero secrets.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/diagnostics

### [ ] discovery-update-info — Use discovery to update network info
**Requires:** When a re-discovery (mDNS/SSDP/DHCP) finds a known device at a new IP/host, the integration updates the existing config entry rather than creating a duplicate.
**Verify by:** `async_step_<discovery_type>` finds the existing entry by unique ID and calls `self.hass.config_entries.async_update_entry(..., data={...})` before aborting with `already_configured`. Exempt if no discovery.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/discovery-update-info

### [ ] discovery — Devices can be discovered
**Requires:** The integration supports at least one discovery method appropriate to the protocol — Zeroconf, SSDP, DHCP, USB, Bluetooth, etc. — declared in `manifest.json` (`"zeroconf"`, `"ssdp"`, …) with a matching step in the config flow.
**Verify by:** `manifest.json` declares a discovery protocol and `config_flow.py` implements the corresponding `async_step_zeroconf` / `async_step_ssdp` / `async_step_dhcp`. Pure cloud integrations mark **exempt**.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/discovery

### [ ] docs-data-update — Document how data is updated
**Requires:** Docs explain the update mechanism (polling at X seconds, push events, websocket subscription) so users understand latency and whether to tune intervals.
**Verify by:** Look for a `## How it works` / `## Update mechanism` section covering poll cadence and any push channels.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/docs-data-update

### [ ] docs-examples — Provide automation examples
**Requires:** Docs include at least one realistic automation/script YAML example using the integration's entities, events, or services.
**Verify by:** Look for a `## Automation examples` / `## Automations` section with triple-fenced YAML blocks.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/docs-examples

### [ ] docs-known-limitations — Document known limitations
**Requires:** Docs list limitations that are not obvious bugs — things the integration cannot do, vendor constraints, protocol gaps.
**Verify by:** Look for a `## Known limitations` / `## Limitations` section enumerating at least the obvious gaps.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/docs-known-limitations

### [ ] docs-supported-devices — Document supported (and unsupported) devices
**Requires:** Docs list which device models are known to work, which are known not to work, and how a user can check compatibility.
**Verify by:** Look for a `## Supported devices` table or list with model names. A short rationale for unsupported models is a plus.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/docs-supported-devices

### [ ] docs-supported-functions — Document supported functionality
**Requires:** Docs enumerate every entity/sensor/service the integration exposes, with units and meaning.
**Verify by:** Look for a `## Features` / `## Entities` section with one line per entity or an entity table.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/docs-supported-functions

### [ ] docs-troubleshooting — Provide troubleshooting guidance
**Requires:** Docs have a troubleshooting section covering common failure modes: connection errors, auth errors, how to enable debug logs, where to file a bug report.
**Verify by:** Look for a `## Troubleshooting` section with at least: enabling debug logs (via `logger:` YAML), downloading diagnostics, and where to open an issue.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/docs-troubleshooting

### [ ] docs-use-cases — Describe integration use cases
**Requires:** Docs outline typical use cases — what problems the integration solves, real-world scenarios.
**Verify by:** Opening sections or a `## Use cases` block explain who this is for and what they would do with it.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/docs-use-cases

### [ ] dynamic-devices — Add devices that appear after setup
**Requires:** If the user adds a new device to their account/hub after the integration is set up, the new device appears in HA on the next refresh — no reload required.
**Verify by:** In the coordinator's update path, detect new device IDs and call `async_add_entities(...)` via a listener registered during `async_setup_entry`. Exempt for single-device integrations.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/dynamic-devices

### [ ] entity-category — Entities assigned appropriate `EntityCategory`
**Requires:** Configuration and diagnostic entities set `_attr_entity_category = EntityCategory.CONFIG` or `EntityCategory.DIAGNOSTIC`. Primary sensing entities leave this unset.
**Verify by:** Grep entity classes for `_attr_entity_category`. Settings/debug entities must be categorized; primary measurements must not be.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-category

### [ ] entity-device-class — Entities use device classes where possible
**Requires:** Entities set `_attr_device_class` to a standard class (`SensorDeviceClass.VOLTAGE`, `BinarySensorDeviceClass.POWER`, etc.) whenever one applies. This drives icons, unit rendering, and voice.
**Verify by:** Grep every entity class for `_attr_device_class`. Entities with a matching class in `homeassistant.components.<platform>.const` should declare it.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-device-class

### [ ] entity-disabled-by-default — Disable noisy/less-popular entities
**Requires:** Rarely-useful, high-churn, or diagnostic entities set `_attr_entity_registry_enabled_default = False` so the DB isn't flooded by default. The user can enable them manually.
**Verify by:** Identify high-frequency / low-value entities (debug counters, raw samples) and confirm `_attr_entity_registry_enabled_default = False`. Primary entities remain enabled.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-disabled-by-default

### [ ] entity-translations — Entity names are translated
**Requires:** Every entity uses `_attr_translation_key` and has a matching entry under `entity.<platform>.<key>.name` in `strings.json` and all shipped translation files.
**Verify by:** Grep entities for `_attr_translation_key`. Cross-check each key exists in `strings.json`. Every `translations/<lang>.json` should contain the same keys.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-translations

### [ ] exception-translations — Exception messages are translatable
**Requires:** User-facing exceptions (`HomeAssistantError`, `ServiceValidationError`) use `translation_domain=DOMAIN` and `translation_key=...` so the message text comes from the translation files.
**Verify by:** Grep for `HomeAssistantError(` / `ServiceValidationError(`. Each should pass `translation_key=` rather than a hard-coded string. `strings.json` should have an `exceptions` or `errors` section matching those keys.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/exception-translations

### [ ] icon-translations — Implement icon translations
**Requires:** State-dependent or multi-variant icons are declared in `icons.json` (per-entity, per-state), not hard-coded in Python. Enables community icon overrides and keeps Python clean.
**Verify by:** Check for `custom_components/<domain>/icons.json`. Entities that vary their icon by state should map those states under `entity.<platform>.<key>.state.<state>` there, not via `_attr_icon` logic.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/icon-translations

### [ ] reconfiguration-flow — Reconfigure flow available
**Requires:** `async_step_reconfigure` is implemented. Users can change connection details (host, credentials) without deleting and re-adding the entry.
**Verify by:** Grep `config_flow.py` for `async_step_reconfigure`. From the UI, the integration's `⋮` menu must show **Reconfigure**.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/reconfiguration-flow

### [ ] repair-issues — Use repair issues for user intervention
**Requires:** When the integration needs the user to act (expired credentials, disabled feature, unsupported firmware), it creates a repair issue via `async_create_issue` / repair flow — not a silent log.
**Verify by:** Grep for `ir.async_create_issue` or `async_create_issue`. Non-trivial user-visible failure modes should create a repair. `strings.json → issues` contains matching entries.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/repair-issues

### [ ] stale-devices — Remove stale devices
**Requires:** When a device disappears from the account/hub (user deletes it, moves it), the integration removes it from HA's device registry on the next update.
**Verify by:** The coordinator or an `async_remove_config_entry_device` implementation compares current API devices to the device registry and calls `device_registry.async_remove_device` for stale entries. Exempt for single-device integrations.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/stale-devices

---

## Platinum — 3 rules (additional, on top of Gold)

### [ ] async-dependency — Dependency is async
**Requires:** The third-party library used to talk to the device/service is natively asyncio-based (no `run_in_executor` wrapping of a sync client).
**Verify by:** Read the imports and library source. If every I/O call is already `await`-able, pass. If the integration wraps a sync client in `hass.async_add_executor_job`, fail.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/async-dependency

### [ ] inject-websession — Dependency accepts an injected aiohttp session
**Requires:** The library accepts an `aiohttp.ClientSession` passed in from the integration (via `async_get_clientsession(hass)`), instead of creating its own. This reuses HA's connection pool and cookie jar.
**Verify by:** In `async_setup_entry`, `session = async_get_clientsession(hass)` is passed to the client constructor. The library must expose a `session=` (or equivalent) parameter.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/inject-websession

### [ ] strict-typing — Strict typing
**Requires:** The entire integration passes **strict** `mypy` / type-checker runs with no `Any`, no implicit `Optional`, full return-type annotations, and typed `ConfigEntry` (`ConfigEntry[RuntimeDataType]`).
**Verify by:** Run `mypy --strict custom_components/<domain>` (or the core `script/mypy` helper). Zero errors required. The PR should also add the domain to the core's strict-typing allow-list.
**Reference:** https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/strict-typing

---

## Appendix: One-shot audit checklist (flat)

Copy this block into a PR description or an issue template when proposing a tier bump.

### Bronze (18)
- [ ] Bronze: `action-setup` — Service actions registered in `async_setup`
- [ ] Bronze: `appropriate-polling` — Appropriate polling interval
- [ ] Bronze: `brands` — Branding assets submitted
- [ ] Bronze: `common-modules` — Common patterns in `coordinator.py` / `entity.py`
- [ ] Bronze: `config-flow-test-coverage` — 100% config-flow test coverage
- [ ] Bronze: `config-flow` — UI-based setup via `config_flow`
- [ ] Bronze: `dependency-transparency` — Dependencies are transparent / PyPI-sourced
- [ ] Bronze: `docs-actions` — Docs describe service actions
- [ ] Bronze: `docs-high-level-description` — Docs open with a high-level description
- [ ] Bronze: `docs-installation-instructions` — Docs provide step-by-step install
- [ ] Bronze: `docs-removal-instructions` — Docs describe removal / cleanup
- [ ] Bronze: `entity-event-setup` — Entity events use `async_added_to_hass` lifecycle
- [ ] Bronze: `entity-unique-id` — Entities have a stable unique ID
- [ ] Bronze: `has-entity-name` — Entities set `_attr_has_entity_name = True`
- [ ] Bronze: `runtime-data` — Per-entry state in `ConfigEntry.runtime_data`
- [ ] Bronze: `test-before-configure` — Config flow validates the connection
- [ ] Bronze: `test-before-setup` — Setup raises `ConfigEntryNotReady` / `AuthFailed`
- [ ] Bronze: `unique-config-entry` — Duplicate entries prevented

### Silver (10)
- [ ] Silver: `action-exceptions` — Services raise on failure
- [ ] Silver: `config-entry-unloading` — `async_unload_entry` implemented
- [ ] Silver: `docs-configuration-parameters` — Docs describe options
- [ ] Silver: `docs-installation-parameters` — Docs describe install params
- [ ] Silver: `entity-unavailable` — Entities marked unavailable when offline
- [ ] Silver: `integration-owner` — `codeowners` set in manifest
- [ ] Silver: `log-when-unavailable` — Log once on down, once on recovery
- [ ] Silver: `parallel-updates` — `PARALLEL_UPDATES` declared per platform
- [ ] Silver: `reauthentication-flow` — Reauth flow implemented
- [ ] Silver: `test-coverage` — >95% overall test coverage

### Gold (21)
- [ ] Gold: `devices` — Entities grouped under `DeviceInfo`
- [ ] Gold: `diagnostics` — Diagnostics export with redaction
- [ ] Gold: `discovery-update-info` — Discovery updates existing entry
- [ ] Gold: `discovery` — Discovery protocol declared and handled
- [ ] Gold: `docs-data-update` — Docs describe data-update mechanism
- [ ] Gold: `docs-examples` — Docs include automation examples
- [ ] Gold: `docs-known-limitations` — Docs list known limitations
- [ ] Gold: `docs-supported-devices` — Docs list supported models
- [ ] Gold: `docs-supported-functions` — Docs enumerate features/entities
- [ ] Gold: `docs-troubleshooting` — Docs have troubleshooting section
- [ ] Gold: `docs-use-cases` — Docs describe use cases
- [ ] Gold: `dynamic-devices` — New devices appear without reload
- [ ] Gold: `entity-category` — Entities assigned `EntityCategory`
- [ ] Gold: `entity-device-class` — Entities use standard device classes
- [ ] Gold: `entity-disabled-by-default` — Noisy entities disabled by default
- [ ] Gold: `entity-translations` — Entity names translated via `translation_key`
- [ ] Gold: `exception-translations` — Exceptions use `translation_key`
- [ ] Gold: `icon-translations` — Icons declared in `icons.json`
- [ ] Gold: `reconfiguration-flow` — Reconfigure flow implemented
- [ ] Gold: `repair-issues` — Repair issues created for user intervention
- [ ] Gold: `stale-devices` — Stale devices removed from registry

### Platinum (3)
- [ ] Platinum: `async-dependency` — Library is natively async
- [ ] Platinum: `inject-websession` — Library accepts injected `aiohttp.ClientSession`
- [ ] Platinum: `strict-typing` — Integration passes `mypy --strict`
