# --- Project Information ---
# Project: UUV Simulation Framework
# Version: 1.0.0
# Date: November 2025
# 
# --- Authors and Contributors ---
# Primary:
# - Gunner Cook-Dumas (SCRUM Manager, Backend, Agent, Model, and GA Stucture)
# - Justin Mosman (developer)
# - Michael Cardinal (developer)
# 
# Secondary:
# - Lauren Milne (SCRUM Product Owner)
# 
# --- Reviewers/Bosses ---
# - Prof. Lance Fiondella, ECE, University of Massachusetts Dartmouth
# - Prof. Hang Dinh, CIS, Indiana University South Bend

from __future__ import annotations
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple, Any
import json

from agents import model
#=====================================================================================================================
#=====================================================================================================================
# ConfigManager class, used to house config specific functionality
class ConfigManager:
    def __init__(
        self,
        default_dir: Optional[str | Path] = "configs",  # path to a directory for saved configs (created if requested).
        file_ext: str = ".json",  # extension used for the saved file
        schema_version: str = "1.0",  # version string that will be added to the json for bookkeeping
        create_dir: bool = True,  # whether to create a directory to save file if one doesn't exist
        allow_overwrite: bool = False,  # whether save operations may overwrite existing files by default.
    ):
        # normalize path
        self.config_dir = Path(default_dir).expanduser()
        self.file_ext = file_ext if file_ext.startswith(".") else f".{file_ext}"
        self.schema_version = str(schema_version)
        self.allow_overwrite = bool(allow_overwrite)

        # Create directory if requested
        if create_dir:
            try:
                self.config_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                # directory creation failing is not fatal here, but we keep the path
                # for later save attempts which can raise clearer IO errors
                # Keep a simple attribute to indicate creation attempted
                self._mkdir_error = e
            else:
                self._mkdir_error = None
        else:
            self._mkdir_error = None

        # Try to discover known agent types from the UUVModel mapping.
        # This is optional — if importing or introspecting the model fails,
        # we fall back to an empty list and validations will be lenient.
        try:
            # model.UUVModel is expected to exist
            self._known_agent_types = list(model.UUVModel.AGENT_MAP.keys())
        except Exception:
            # defensive fallback
            self._known_agent_types = []

        # small runtime metadata
        self.created_at = datetime.utcnow().isoformat() + "Z"
        # a quick sanity flag to indicate manager is ready for save/load actions
        self.ready = True

    #Helper function to return a list of agent types from the model
    def known_agent_types(self) -> List[str]:
        """Return a list of agent type names discovered from the model (may be empty)."""
        return list(self._known_agent_types)

    # Function to return a default filepath for saving the configs 
    def default_filepath(self, name: Optional[str] = None) -> Path:
        """
        Return a timestamped default file path for saving a config.
        Example: configs/spawn_config_20251106T142500.json
        """
        base = name or "spawn_config"
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        filename = f"{base}_{timestamp}{self.file_ext}"
        return self.config_dir / filename

    # Helper function to return a normalized position as a list of two integers
    def _normalize_pos(self, pos: Any) -> Tuple[bool, Any]:
        """
        Normalize a position value to a list of two ints.
        Returns (ok, normalized_or_error_message)
        """
        # Accept [x, y] or (x, y) where values are ints/convertible to int
        if not isinstance(pos, (list, tuple)):
            return False, "pos must be a list or tuple"
        if len(pos) != 2:
            return False, "pos must have length 2"
        try:
            x = int(pos[0])
            y = int(pos[1])
        except Exception:
            return False, "pos coordinates must be integers"
        return True, [x, y]

    # Function to take the spawns structure and normalize it so that it can be used correctly
    # while perserving the metadata as well
    def _validate_and_normalize_spawns(self, spawns: Any) -> Tuple[dict, List[str]]:
        """
        Validate the top-level spawns structure and normalize entries.
        Returns (normalized_spawns, warnings)
        Normalized structure keeps the same outer keys but ensures each spawn
        entry is a dict with 'type' (str) and 'pos' ([int,int]) and preserves optional fields.
        """
        warnings: List[str] = []
        normalized: dict = {}

        if not isinstance(spawns, dict):
            raise TypeError("spawns must be a dict mapping categories to lists of spawn entries")

        for category, entries in spawns.items():
            if not isinstance(category, str):
                warnings.append(f"Skipping non-string category key: {category!r}")
                continue
            if entries is None:
                continue
            if not isinstance(entries, (list, tuple)):
                warnings.append(f"Category '{category}' value is not a list; skipping")
                continue

            normalized_list = []
            for idx, item in enumerate(entries):
                # Item may be [x,y], or dict with 'type' and 'pos'
                if isinstance(item, (list, tuple)):
                    # assume just position, type unknown
                    ok, res = self._normalize_pos(item)
                    if not ok:
                        warnings.append(f"{category}[{idx}]: invalid pos - {res}; skipping")
                        continue
                    spawn_entry = {"type": None, "pos": res}
                elif isinstance(item, dict):
                    # require a 'pos'
                    pos = item.get("pos")
                    if pos is None:
                        warnings.append(f"{category}[{idx}]: missing 'pos'; skipping")
                        continue
                    ok, res = self._normalize_pos(pos)
                    if not ok:
                        warnings.append(f"{category}[{idx}]: invalid pos - {res}; skipping")
                        continue
                    spawn_entry = {"type": item.get("type"), "pos": res}
                    # preserve optional fields (name, group_id, etc.)
                    for k, v in item.items():
                        if k not in ("type", "pos"):
                            spawn_entry[k] = v
                else:
                    warnings.append(f"{category}[{idx}]: unsupported entry type {type(item).__name__}; skipping")
                    continue

                # Validate type if we know the known agent types
                if spawn_entry.get("type") is None:
                    warnings.append(f"{category}[{idx}]: 'type' is missing or None")
                else:
                    if self._known_agent_types and spawn_entry["type"] not in self._known_agent_types:
                        warnings.append(f"{category}[{idx}]: unknown agent type '{spawn_entry['type']}'")

                normalized_list.append(spawn_entry)

            if normalized_list:
                normalized[category] = normalized_list

        return normalized, warnings
    
    # Save function that is used to save the "spawns" dict to the json
    def save(self, spawns: dict, path: Optional[str | Path] = None, validate: bool = True, map_file_path: str = None) -> Tuple[Path, List[str]]:
        """
        Save `spawns` to JSON on disk.

        Args:
            spawns: dict mapping category -> list of spawn entries (see examples).
            path: optional path or filename to save to. If None, uses `default_filepath()`.
            validate: whether to run basic validation/normalization (recommended True).

        Returns:
            (saved_path, warnings) where warnings is a list of strings describing non-fatal issues.
        Raises:
            TypeError, ValueError, FileExistsError, OSError on severe errors.
        """
        # Choose path
        if path is None:
            out_path = self.default_filepath()
        else:
            out_path = Path(path).expanduser()
            # ensure extension
            if out_path.suffix == "":
                out_path = out_path.with_suffix(self.file_ext)

        # If directory doesn't exist, try to create
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise OSError(f"Couldn't ensure directory for save path {out_path.parent}: {e}") from e

        # Prevent overwrite if requested
        if out_path.exists() and not self.allow_overwrite:
            raise FileExistsError(f"File {out_path} already exists and allow_overwrite is False")

        # Validate / normalize
        warnings: List[str] = []
        normalized_spawns = spawns
        if validate:
            try:
                normalized_spawns, warnings = self._validate_and_normalize_spawns(spawns)
            except Exception as e:
                raise ValueError(f"Validation failed: {e}") from e

        # Strip map_file_path so that it will work on every project
        # ex: C:/Users/Daniel/Desktop/Research/Simulation-Software/data/shape_files/Harbour_Depth_Area.shp -> data/shape_files/Harbour_Depth_Area.shp
        relative_map_path = ""
        if len(map_file_path) > 0:
            marker = "Simulation-Software/"
            idx = map_file_path.find(marker)
            if idx != -1:
                relative_map_path = map_file_path[idx + len(marker):]
            else:
                relative_map_path = map_file_path
 
        # Build payload
        payload = {
            "schema_version": self.schema_version,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "generator": "ConfigManager",
            "map_file": relative_map_path,
            "spawns": normalized_spawns,
        }

        # Write JSON safely
        try:
            with open(out_path, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2, ensure_ascii=False)
        except Exception as e:
            raise OSError(f"Failed to write config to {out_path}: {e}") from e

        return out_path, warnings
    
    # Load function to load the data from the config and return its contents
    def load(self, path, validate_fn=None, remove_invalid: bool = True, allow_unknown_types: bool = False):
        """
        Load a spawn config file and return (spawns_dict, warnings, metadata).

        Args:
            path: path or str to the JSON config file.
            validate_fn: optional callable to validate each spawn entry.
                Expected signature: validate_fn(spawn_entry) -> bool | (bool, str|None)
                If it returns (False, "reason") the entry is treated as invalid.
            remove_invalid: if True, invalid entries from validate_fn are removed from the returned spawns.
            allow_unknown_types: if True, warnings about unknown agent types (from internal validation)
                will be suppressed.

        Returns:
            (normalized_spawns: dict, warnings: List[str], metadata: dict)

        Raises:
            FileNotFoundError, ValueError, OSError on read/parse errors.
        """
        p = Path(path).expanduser()
        if not p.exists():
            raise FileNotFoundError(f"Config file not found: {p}")

        try:
            with open(p, "r", encoding="utf-8") as fh:
                payload = json.load(fh)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config {p}: {e}") from e
        except Exception as e:
            raise OSError(f"Failed to read config file {p}: {e}") from e

        metadata = {
            "schema_version": payload.get("schema_version"),
            "created_at": payload.get("created_at"),
            "generator": payload.get("generator"),
            "loaded_from": str(p),
            "map_file_path": payload.get("map_file")
        }

        raw_spawns = payload.get("spawns")
        if raw_spawns is None:
            raise ValueError(f"No 'spawns' key found in config {p}")

        # Normalize & basic validation using existing helper
        normalized_spawns, warnings = self._validate_and_normalize_spawns(raw_spawns)

        # Optionally suppress unknown-type warnings
        if allow_unknown_types and warnings:
            warnings = [w for w in warnings if "unknown agent type" not in w]

        # If an external validation function is provided, run it per-entry.
        # validate_fn is expected to return either bool or (bool, message).
        if validate_fn is not None:
            extra_warnings: List[str] = []
            for category in list(normalized_spawns.keys()):
                entries = normalized_spawns[category]
                kept_entries = []
                for idx, entry in enumerate(entries):
                    try:
                        res = validate_fn(entry)
                    except Exception as e:
                        # If validator crashes, treat as invalid and warn
                        ok = False
                        msg = f"validator error: {e}"
                    else:
                        if isinstance(res, tuple):
                            ok, msg = bool(res[0]), (res[1] if len(res) > 1 else None)
                        else:
                            ok, msg = bool(res), None

                    if ok:
                        kept_entries.append(entry)
                    else:
                        extra_warnings.append(f"{category}[{idx}]: external validation failed - {msg or 'unspecified'}; entry removed")
                if kept_entries:
                    normalized_spawns[category] = kept_entries
                else:
                    # remove empty category
                    normalized_spawns.pop(category, None)
            warnings.extend(extra_warnings)

        return normalized_spawns, warnings, metadata