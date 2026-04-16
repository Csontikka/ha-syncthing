# Syncthing Extended — HA Quality Scale állapot

> Reference: `docs/HA_QUALITY_SCALE_CHECKLIST.md`
> Domain: `syncthing_extended` · Verzió: `0.1.7` · Utolsó felmérés: 2026-04-16
>
> Jelmagyarázat: ✅ kész · ⚠️ részleges · ❌ hiányzik · ⛔ exempt · ❓ mérni kell

## Jelenlegi szint

**Bronze: 18/18 ✅** · **Silver: 10/10 ✅** · **Gold: ~10/21** · **Platinum: 2/3 (1 ellenőrizendő)**

Bronze és Silver **lezárva** (2026-04-16): 190 teszt zöld, **100% coverage** minden modulon (`config_flow.py` is), `entity.py` kivonva. **Gold** komoly munka (~8-10 hiány), **Platinum** csak `mypy --strict` pass kell.

---

## Bronze — 18 rule

| # | Rule | Állapot | Megjegyzés |
|---|------|---------|------------|
| 1 | `action-setup` | ✅ | `_async_register_services` hívás `async_setup`-ban (`__init__.py:41`) |
| 2 | `appropriate-polling` | ✅ | `update_interval=timedelta(seconds=scan_interval)`, 10-300s user-konfigurálható |
| 3 | `brands` | ⚠️ | `home-assistant/brands` PR botja lezárta (custom integrationt nem fogad). HA 2026.3+ módszer használva: `custom_components/syncthing_extended/brand/icon.png` + `icon@2x.png`. Custom integration esetén ez **elfogadott megoldás**, de szigorú olvasat szerint hivatalos brands elfogadás nélkül részleges. |
| 4 | `common-modules` | ✅ | `coordinator.py` + `entity.py` (3 base class: `SyncthingSystemEntity`, `SyncthingFolderEntity`, `SyncthingDeviceEntity`). Duplikáció kivonva sensor/binary_sensor/button-ből. |
| 5 | `config-flow-test-coverage` | ✅ | **100% coverage** `config_flow.py`-on (`tests/test_config_flow.py`) |
| 6 | `config-flow` | ✅ | `"config_flow": true` + `async_step_user` működik |
| 7 | `dependency-transparency` | ✅ | Egyetlen requirement: `aiohttp>=3.8.0` — PyPI-n open-source |
| 8 | `docs-actions` | ✅ | README `## Services` szekció 8 service-szel |
| 9 | `docs-high-level-description` | ✅ | README első bekezdése tisztán leírja |
| 10 | `docs-installation-instructions` | ✅ | `## Installation` (HACS + Manual) + `## Configuration` |
| 11 | `docs-removal-instructions` | ✅ | `## Removal` szekció |
| 12 | `entity-event-setup` | ⛔ | Exempt — coordinator-based, nincs manual event subscription |
| 13 | `entity-unique-id` | ✅ | `f"{entry_id}_..."` minden entitáson, stabil |
| 14 | `has-entity-name` | ✅ | `_attr_has_entity_name = True` minden osztályon |
| 15 | `runtime-data` | ✅ | `entry.runtime_data = coordinator`, típusolt `SyncthingConfigEntry = ConfigEntry[SyncthingCoordinator]` |
| 16 | `test-before-configure` | ✅ | `check_health()` + `get_system_status()` hívás entry létrehozás előtt, `cannot_connect`/`invalid_auth`/`ssl_error` hibákra mappelve |
| 17 | `test-before-setup` | ✅ | `async_config_entry_first_refresh()`, coordinator `ConfigEntryAuthFailed` / `UpdateFailed` raise |
| 18 | `unique-config-entry` | ✅ | `async_set_unique_id(myID)` + `_abort_if_unique_id_configured()` |

**Bronze lezárva ✅** · #3 `brands` továbbra is ⚠️ (hivatalos `home-assistant/brands` PR nem mergelhető custom integrationre, de HA 2026.3+ local brand module elfogadott megoldás).

---

## Silver — 10 rule

| # | Rule | Állapot | Megjegyzés |
|---|------|---------|------------|
| 1 | `action-exceptions` | ✅ | Minden service `raise HomeAssistantError(...)` on failure |
| 2 | `config-entry-unloading` | ✅ | `async_unload_entry` → `async_unload_platforms`. Services globálisak (`async_setup`-ban), nem kell unregister. |
| 3 | `docs-configuration-parameters` | ✅ | README `### Options` — scan_interval dokumentálva |
| 4 | `docs-installation-parameters` | ✅ | Host/Port/API Key/SSL/Verify SSL dokumentálva `### Finding your API key`-vel együtt |
| 5 | `entity-unavailable` | ✅ | Minden entitás `CoordinatorEntity` — `last_update_success` automatikus |
| 6 | `integration-owner` | ✅ | `"codeowners": ["@csontikka"]` |
| 7 | `log-when-unavailable` | ✅ | Coordinator `UpdateFailed`-et raise-el, framework dedup-ol |
| 8 | `parallel-updates` | ✅ | `PARALLEL_UPDATES = 1` sensor/binary_sensor/button-ben |
| 9 | `reauthentication-flow` | ✅ | `async_step_reauth_confirm` + coordinator `ConfigEntryAuthFailed` |
| 10 | `test-coverage` | ✅ | **100% coverage** mindegyik modulon (190 teszt, 746 stmts, 0 miss). Silver küszöb >95% bőven teljesítve. |

**Silver lezárva ✅**

---

## Gold — 21 rule

| # | Rule | Állapot | Megjegyzés |
|---|------|---------|------------|
| 1 | `devices` | ✅ | `_attr_device_info` minden entitáson, `(DOMAIN, entry_id)` + per-folder/per-device `via_device` hierarchia |
| 2 | `diagnostics` | ✅ | `diagnostics.py` `async_redact_data` használattal, `CONF_API_KEY`/`myID`/`deviceID`/`address` redacted |
| 3 | `discovery-update-info` | ⛔ | Exempt — nincs discovery |
| 4 | `discovery` | ⛔ | Exempt — Syncthing local API, nincs standard discovery protokoll (zeroconf/ssdp/dhcp egyike sem) |
| 5 | `docs-data-update` | ⚠️ | Scan interval említve `### Options`-ben, de **dedikált `## How it works` nincs** |
| 6 | `docs-examples` | ✅ | README `### Example automation` YAML blokkokkal |
| 7 | `docs-known-limitations` | ❌ | Nincs `## Known limitations` szekció |
| 8 | `docs-supported-devices` | ⛔ | Exempt — ez service integration, nem device-alapú. De érdemes megjegyezni a "Supported versions" szekcióban hogy a Syncthing verziók miket támogatnak |
| 9 | `docs-supported-functions` | ✅ | README `## Entities` — System/Per folder/Per device bontva |
| 10 | `docs-troubleshooting` | ✅ | `## Troubleshooting` → Diagnostics Export + Debug Logs |
| 11 | `docs-use-cases` | ⚠️ | `## Why this instead of the built-in integration?` megközelíti, de **explicit `## Use cases` hiányzik** |
| 12 | `dynamic-devices` | ❌ | Új folder/device Syncthing oldalon → HA-ban **csak reload után** jelenik meg. Az entitás-lista `async_setup_entry`-ben épül, nincs `async_add_entities` listener a coordinator update path-on. |
| 13 | `entity-category` | ✅ | `EntityCategory.DIAGNOSTIC` korrekten használva (version, uptime, device_id, stb.) |
| 14 | `entity-device-class` | ✅ | `SensorDeviceClass.DURATION/DATA_SIZE/TIMESTAMP`, `BinarySensorDeviceClass.CONNECTIVITY/PROBLEM/MOVING` |
| 15 | `entity-disabled-by-default` | ❌ | Egyetlen `_attr_entity_registry_enabled_default = False` sincs. Jelöltek: `goroutines`, `alloc_bytes`, `sequence`, `global_*`, `in_sync_*`, `local_*` diagnostic sensorok |
| 16 | `entity-translations` | ✅ | Minden entitás `translation_key` + `strings.json` `entity.<platform>.<key>.name` meg van |
| 17 | `exception-translations` | ❌ | `HomeAssistantError(f"Failed to scan folder {folder_id}")` — hardcoded string, nincs `translation_key=` + `strings.json → exceptions` |
| 18 | `icon-translations` | ❌ | Nincs `icons.json`. Ikonok `icon="mdi:..."` hardcoded Python-ban |
| 19 | `reconfiguration-flow` | ❌ | Nincs `async_step_reconfigure` — host/port változtatáshoz törölni + újrahozzáadni kell |
| 20 | `repair-issues` | ❌ | Nincs `async_create_issue`. Kiváltó ok lehetne: built-in Syncthing integration is aktív (most csak `_LOGGER.warning`) |
| 21 | `stale-devices` | ❌ | Folder/device eltűnése Syncthingből nem törli az HA device registryből |

**Tennivaló Gold szinten (prioritás szerint):**
1. Dokumentáció: `## Known limitations`, `## Use cases`, `## How it works` szekciók a README-be
2. `entity-disabled-by-default`: alacsony értékű diagnostic sensorokra `_attr_entity_registry_enabled_default = False`
3. `reconfiguration-flow`: `async_step_reconfigure` implementáció config_flow-ban (viszonylag olcsó)
4. `exception-translations`: `HomeAssistantError(translation_domain=DOMAIN, translation_key="scan_folder_failed", ...)` + strings.json exceptions block
5. `icon-translations`: `icons.json` generálás, Python ikonok eltávolítása
6. `repair-issues`: built-in Syncthing együttfutásra repair issue (a warning helyett)
7. `dynamic-devices`: coordinator update path-on új folder/device detektálás + `async_add_entities` hívás
8. `stale-devices`: coordinator update-kor registry sync

---

## Platinum — 3 rule

| # | Rule | Állapot | Megjegyzés |
|---|------|---------|------------|
| 1 | `async-dependency` | ✅ | `aiohttp` natív async, sehol `run_in_executor` |
| 2 | `inject-websession` | ✅ | `async_get_clientsession(hass)` átadva az `SyncthingApi`-nak mindkét helyen (`__init__.py:56` + `config_flow.py:65`) |
| 3 | `strict-typing` | ❓ | **Mérni kell**: `mypy --strict custom_components/syncthing_extended`. A `type SyncthingConfigEntry = ConfigEntry[SyncthingCoordinator]` alias már megvan, sok típus annotáció megvan, de `Any` és `Exception`-catch blokkok jelen vannak — kérdéses hogy strict pass-olna-e |

**Tennivaló Platinum szinten:** #3 `mypy --strict` lefuttatása, hibák javítása.

---

## Javasolt sorrend

### 1. lépés — Bronze + Silver lezárás (gyors) ✅ KÉSZ (2026-04-16)
- [x] Coverage futtatás: `pytest --cov=custom_components.syncthing_extended --cov-report=term-missing`
- [x] `entity.py` kivonás — közös 3 base class (system/folder/device)
- [x] Coverage gap betöltés → **100%** minden modulon, 190 teszt zöld

### 2. lépés — Gold dokumentációs rész (olcsó)
- [ ] README: `## Known limitations`, `## Use cases`, `## How it works` új szekciók
- [ ] `entity-disabled-by-default` a diagnostic sensorok egy részén

### 3. lépés — Gold kódolási rész
- [ ] `async_step_reconfigure` + strings.json reconfigure step
- [ ] `exception-translations` — service raise-ek `translation_key`-vel
- [ ] `icons.json` — ikonok átköltöztetése

### 4. lépés — Gold haladó
- [ ] `repair-issues` — built-in Syncthing együttfutásra
- [ ] `dynamic-devices` — coordinator update-kor új folder/device detektálás
- [ ] `stale-devices` — eltűnt folder/device registry eltávolítás

### 5. lépés — Platinum
- [ ] `mypy --strict` futtatás + javítások

---

## `quality_scale.yaml` (javaslat manifest.json mellé mikor ideérünk)

```yaml
rules:
  # Bronze
  action-setup: done
  appropriate-polling: done
  brands: { status: done, comment: "HA 2026.3+ local brand/ folder method" }
  common-modules: done
  config-flow-test-coverage: done
  config-flow: done
  dependency-transparency: done
  docs-actions: done
  docs-high-level-description: done
  docs-installation-instructions: done
  docs-removal-instructions: done
  entity-event-setup: { status: exempt, comment: "coordinator-based" }
  entity-unique-id: done
  has-entity-name: done
  runtime-data: done
  test-before-configure: done
  test-before-setup: done
  unique-config-entry: done
  # Silver
  action-exceptions: done
  config-entry-unloading: done
  docs-configuration-parameters: done
  docs-installation-parameters: done
  entity-unavailable: done
  integration-owner: done
  log-when-unavailable: done
  parallel-updates: done
  reauthentication-flow: done
  test-coverage: done
```
