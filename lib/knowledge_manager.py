#!/usr/bin/env python3
"""
Knowledge Base Manager

JSON-based knowledge base management.

Usage:
    python lib/knowledge_manager.py <command> [options]

Commands:
    # Evasion Techniques
    list-evasion [--type TYPE] [--complexity LEVEL]
    get-evasion --id ID
    add-evasion --name NAME --type TYPE --description DESC [options]
    update-evasion --id ID [options]

    # Loader Components
    get-components [--type TYPE]
    add-component --type TYPE --name NAME --description DESC [options]

    # Scenarios
    list-scenarios [--status STATUS]
    add-scenario --name NAME --storage ID --allocator ID --copier ID --executor ID [options]
    update-scenario --id ID --status STATUS [options]

    # Combinations
    random-combination [--complexity LEVEL]

    # Statistics
    stats

    # Export/Import
    export --output FILE
    import --input FILE
"""

import json
import argparse
import random
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any


class KnowledgeManager:
    """JSON知识库管理"""

    def __init__(self, base_path: str = "knowledge-base"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.files = {
            "evasion": self.base_path / "evasion_techniques.json",
            "loader": self.base_path / "loader_techniques.json",
            "scenarios": self.base_path / "scenarios.json"
        }

    def _load_json(self, file_key: str) -> dict:
        """Load JSON file"""
        path = self.files[file_key]
        if path.exists():
            try:
                return json.loads(path.read_text(encoding='utf-8'))
            except json.JSONDecodeError:
                return self._get_default_schema(file_key)
        return self._get_default_schema(file_key)

    def _get_default_schema(self, file_key: str) -> dict:
        """Get default schema for each file type"""
        defaults = {
            "evasion": {
                "version": "1.0",
                "last_updated": None,
                "techniques": []
            },
            "loader": {
                "version": "1.0",
                "last_updated": None,
                "techniques": [],
                "component_library": {
                    "storage_methods": [],
                    "memory_allocators": [],
                    "data_copiers": [],
                    "executors": []
                }
            },
            "scenarios": {
                "version": "1.0",
                "last_updated": None,
                "scenarios": []
            }
        }
        return defaults.get(file_key, {})

    def _save_json(self, file_key: str, data: dict):
        """Save JSON file"""
        data["last_updated"] = datetime.now().isoformat()
        path = self.files[file_key]
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

    # ==================== Evasion Techniques ====================

    def list_evasion_techniques(
        self,
        evasion_type: Optional[str] = None,
        complexity: Optional[str] = None
    ) -> List[dict]:
        """List evasion techniques with optional filters"""
        data = self._load_json("evasion")
        results = data["techniques"]

        if evasion_type:
            results = [t for t in results if t.get("evasion_type") == evasion_type]
        if complexity:
            results = [t for t in results if t.get("complexity") == complexity]

        return results

    def get_evasion_technique(self, technique_id: str) -> Optional[dict]:
        """Get evasion technique by ID"""
        data = self._load_json("evasion")
        for t in data["techniques"]:
            if t.get("id") == technique_id:
                return t
        return None

    def add_evasion_technique(self, technique: dict) -> str:
        """Add new evasion technique"""
        data = self._load_json("evasion")

        # Generate ID
        existing_ids = [t.get("id", "") for t in data["techniques"]]
        num = len([i for i in existing_ids if i.startswith("T")]) + 1
        technique["id"] = f"T{num:03d}"

        # Set defaults
        technique["created_at"] = datetime.now().isoformat()
        technique.setdefault("category", "evasion")
        technique.setdefault("source", "manual")
        technique.setdefault("detection_risk", "unknown")

        data["techniques"].append(technique)
        self._save_json("evasion", data)

        return technique["id"]

    def update_evasion_technique(self, technique_id: str, updates: dict) -> bool:
        """Update evasion technique"""
        data = self._load_json("evasion")
        for t in data["techniques"]:
            if t.get("id") == technique_id:
                t.update(updates)
                t["updated_at"] = datetime.now().isoformat()
                self._save_json("evasion", data)
                return True
        return False

    # ==================== Loader Components ====================

    def get_components(self, component_type: Optional[str] = None) -> dict:
        """Get loader component library"""
        data = self._load_json("loader")
        lib = data.get("component_library", {})

        if component_type:
            valid_types = ["storage_methods", "memory_allocators", "data_copiers", "executors"]
            if component_type in valid_types:
                return {component_type: lib.get(component_type, [])}
            return {}

        return lib

    def add_component(self, component_type: str, component: dict) -> str:
        """Add loader component"""
        valid_types = ["storage_methods", "memory_allocators", "data_copiers", "executors"]
        if component_type not in valid_types:
            raise ValueError(f"Invalid component type: {component_type}")

        data = self._load_json("loader")
        lib = data.setdefault("component_library", {})
        components = lib.setdefault(component_type, [])

        # Generate ID
        prefix = component_type[:3]
        num = len(components) + 1
        component["id"] = f"{prefix}_{num:03d}"

        components.append(component)
        self._save_json("loader", data)

        return component["id"]

    # ==================== Scenarios ====================

    def list_scenarios(self, status: Optional[str] = None) -> List[dict]:
        """List scenarios with optional status filter"""
        data = self._load_json("scenarios")
        results = data["scenarios"]

        if status:
            results = [s for s in results if s.get("status") == status]

        return results

    def add_scenario(
        self,
        name: str,
        storage: str,
        allocator: str,
        copier: str,
        executor: str,
        status: str = "draft"
    ) -> str:
        """Add new scenario"""
        data = self._load_json("scenarios")

        # Generate ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scenario_id = f"scenario_{storage[:4]}_{allocator[:4]}_{executor[:4]}_{timestamp}"

        scenario = {
            "id": scenario_id,
            "name": name,
            "components": {
                "storage": storage,
                "allocator": allocator,
                "copier": copier,
                "executor": executor
            },
            "status": status,
            "feasibility": {
                "theoretical": "pending"
            },
            "detection_risk": "unknown",
            "complexity": "unknown",
            "loaders": [],
            "references": [],
            "created_at": datetime.now().isoformat()
        }

        data["scenarios"].append(scenario)
        self._save_json("scenarios", data)

        return scenario_id

    def update_scenario(
        self,
        scenario_id: str,
        status: Optional[str] = None,
        loader_id: Optional[str] = None,
        notes: Optional[List[str]] = None
    ) -> bool:
        """Update scenario"""
        data = self._load_json("scenarios")
        for s in data["scenarios"]:
            if s.get("id") == scenario_id:
                if status:
                    s["status"] = status
                if loader_id:
                    s["loaders"].append(loader_id)
                if notes:
                    s["feasibility"]["implementation_notes"] = notes
                s["validated_at"] = datetime.now().isoformat()
                self._save_json("scenarios", data)
                return True
        return False

    def add_loader_technique(
        self,
        storage: str,
        allocator: str,
        copier: str,
        executor: str
    ) -> str:
        """Add successful loader technique combination"""
        data = self._load_json("loader")

        # Check if combination exists
        for t in data["techniques"]:
            comp = t.get("components", {})
            if (comp.get("storage") == storage and
                comp.get("allocator") == allocator and
                comp.get("copier") == copier and
                comp.get("executor") == executor):
                # Increment success count
                t["success_count"] = t.get("success_count", 0) + 1
                self._save_json("loader", data)
                return t["id"]

        # Create new technique
        technique_id = f"LT_{len(data['techniques']) + 1:03d}"

        technique = {
            "id": technique_id,
            "name": f"{storage} + {allocator} + {executor}",
            "storage_method": storage,
            "memory_allocation": allocator,
            "data_copy": copier,
            "execution_method": executor,
            "created_at": datetime.now().isoformat(),
            "success_count": 1,
            "fail_count": 0,
            "sources": ["agent_generated"],
            "components": {
                "storage": storage,
                "allocator": allocator,
                "copier": copier,
                "executor": executor
            }
        }

        data["techniques"].append(technique)
        self._save_json("loader", data)

        return technique_id

    # ==================== Random Combination ====================

    def random_combination(self, complexity: Optional[str] = None) -> dict:
        """Generate random component combination"""
        data = self._load_json("loader")
        lib = data.get("component_library", {})

        def filter_by_complexity(items):
            if not complexity:
                return items
            return [i for i in items if i.get("complexity", "simple") == complexity]

        storage_methods = lib.get("storage_methods", [])
        allocators = filter_by_complexity(lib.get("memory_allocators", []))
        copiers = lib.get("data_copiers", [])
        executors = filter_by_complexity(lib.get("executors", []))

        # Fallback if filtered results are empty
        if not allocators:
            allocators = lib.get("memory_allocators", [])
        if not executors:
            executors = lib.get("executors", [])

        result = {
            "storage": random.choice(storage_methods) if storage_methods else None,
            "allocator": random.choice(allocators) if allocators else None,
            "copier": random.choice(copiers) if copiers else None,
            "executor": random.choice(executors) if executors else None
        }

        return result

    def check_combination_exists(
        self,
        storage: str,
        allocator: str,
        copier: str,
        executor: str
    ) -> Optional[dict]:
        """Check if combination already exists in scenarios"""
        data = self._load_json("scenarios")
        for s in data["scenarios"]:
            comp = s.get("components", {})
            if (comp.get("storage") == storage and
                comp.get("allocator") == allocator and
                comp.get("copier") == copier and
                comp.get("executor") == executor):
                return s
        return None

    # ==================== Statistics ====================

    def get_stats(self) -> dict:
        """Get knowledge base statistics"""
        evasion_data = self._load_json("evasion")
        loader_data = self._load_json("loader")
        scenarios_data = self._load_json("scenarios")

        # Count evasion by type
        evasion_by_type = {}
        for t in evasion_data["techniques"]:
            etype = t.get("evasion_type", "unknown")
            evasion_by_type[etype] = evasion_by_type.get(etype, 0) + 1

        # Count scenarios by status
        scenarios_by_status = {}
        for s in scenarios_data["scenarios"]:
            status = s.get("status", "unknown")
            scenarios_by_status[status] = scenarios_by_status.get(status, 0) + 1

        lib = loader_data.get("component_library", {})

        return {
            "evasion_techniques": {
                "total": len(evasion_data["techniques"]),
                "by_type": evasion_by_type
            },
            "loader_components": {
                "storage_methods": len(lib.get("storage_methods", [])),
                "memory_allocators": len(lib.get("memory_allocators", [])),
                "data_copiers": len(lib.get("data_copiers", [])),
                "executors": len(lib.get("executors", []))
            },
            "scenarios": {
                "total": len(scenarios_data["scenarios"]),
                "by_status": scenarios_by_status
            },
            "loader_techniques": len(loader_data.get("techniques", []))
        }

    # ==================== Export/Import ====================

    def export_knowledge(self, output_path: str):
        """Export all knowledge to a single file"""
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "evasion_techniques": self._load_json("evasion"),
            "loader_techniques": self._load_json("loader"),
            "scenarios": self._load_json("scenarios")
        }

        Path(output_path).write_text(
            json.dumps(export_data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

    def import_knowledge(self, input_path: str, merge: bool = True):
        """Import knowledge from file"""
        data = json.loads(Path(input_path).read_text(encoding='utf-8'))

        if merge:
            # Merge with existing data
            for key in ["evasion", "loader", "scenarios"]:
                existing = self._load_json(key)
                imported = data.get(f"{key}_techniques", data.get(key, {}))

                if key == "evasion":
                    existing_ids = {t["id"] for t in existing["techniques"]}
                    for t in imported.get("techniques", []):
                        if t["id"] not in existing_ids:
                            existing["techniques"].append(t)

                elif key == "loader":
                    existing_ids = {t["id"] for t in existing["techniques"]}
                    for t in imported.get("techniques", []):
                        if t["id"] not in existing_ids:
                            existing["techniques"].append(t)
                    # Merge component library
                    lib = existing.setdefault("component_library", {})
                    for comp_type in ["storage_methods", "memory_allocators", "data_copiers", "executors"]:
                        existing_ids = {c["id"] for c in lib.get(comp_type, [])}
                        for c in imported.get("component_library", {}).get(comp_type, []):
                            if c["id"] not in existing_ids:
                                lib.setdefault(comp_type, []).append(c)

                elif key == "scenarios":
                    existing_ids = {s["id"] for s in existing["scenarios"]}
                    for s in imported.get("scenarios", []):
                        if s["id"] not in existing_ids:
                            existing["scenarios"].append(s)

                self._save_json(key, existing)
        else:
            # Replace existing data
            for key in ["evasion", "loader", "scenarios"]:
                self._save_json(key, data.get(f"{key}_techniques", data.get(key, {})))


def main():
    parser = argparse.ArgumentParser(description="Knowledge Base Manager")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # List evasion
    list_evasion = subparsers.add_parser("list-evasion", help="List evasion techniques")
    list_evasion.add_argument("--type", help="Filter by evasion type")
    list_evasion.add_argument("--complexity", help="Filter by complexity")

    # Get evasion
    get_evasion = subparsers.add_parser("get-evasion", help="Get evasion technique by ID")
    get_evasion.add_argument("--id", required=True, help="Technique ID")

    # Add evasion
    add_evasion = subparsers.add_parser("add-evasion", help="Add evasion technique")
    add_evasion.add_argument("--name", required=True, help="Technique name")
    add_evasion.add_argument("--type", required=True, help="Evasion type")
    add_evasion.add_argument("--description", required=True, help="Description")
    add_evasion.add_argument("--code-template", help="Code template")
    add_evasion.add_argument("--apis", help="Comma-separated API list")
    add_evasion.add_argument("--complexity", default="medium", help="Complexity level")
    add_evasion.add_argument("--detection-risk", default="unknown", help="Detection risk")
    add_evasion.add_argument("--references", help="Comma-separated reference URLs")

    # Get components
    get_components = subparsers.add_parser("get-components", help="Get loader components")
    get_components.add_argument("--type", help="Component type (storage_methods, memory_allocators, data_copiers, executors)")

    # Add component
    add_component = subparsers.add_parser("add-component", help="Add loader component")
    add_component.add_argument("--type", required=True, help="Component type")
    add_component.add_argument("--name", required=True, help="Component name")
    add_component.add_argument("--description", required=True, help="Description")
    add_component.add_argument("--apis", help="Comma-separated API list")
    add_component.add_argument("--complexity", default="simple", help="Complexity level")
    add_component.add_argument("--references", help="Comma-separated reference URLs")

    # List scenarios
    list_scenarios = subparsers.add_parser("list-scenarios", help="List scenarios")
    list_scenarios.add_argument("--status", help="Filter by status")

    # Add scenario
    add_scenario = subparsers.add_parser("add-scenario", help="Add scenario")
    add_scenario.add_argument("--name", required=True, help="Scenario name")
    add_scenario.add_argument("--storage", required=True, help="Storage method ID")
    add_scenario.add_argument("--allocator", required=True, help="Allocator ID")
    add_scenario.add_argument("--copier", required=True, help="Copier ID")
    add_scenario.add_argument("--executor", required=True, help="Executor ID")
    add_scenario.add_argument("--status", default="draft", help="Initial status")

    # Update scenario
    update_scenario = subparsers.add_parser("update-scenario", help="Update scenario")
    update_scenario.add_argument("--id", required=True, help="Scenario ID")
    update_scenario.add_argument("--status", help="New status")
    update_scenario.add_argument("--loader-id", help="Loader ID to add")
    update_scenario.add_argument("--notes", help="Implementation notes")

    # Add loader technique
    add_loader = subparsers.add_parser("add-loader-technique", help="Add successful loader technique")
    add_loader.add_argument("--storage", required=True)
    add_loader.add_argument("--allocator", required=True)
    add_loader.add_argument("--copier", required=True)
    add_loader.add_argument("--executor", required=True)

    # Random combination
    random_combo = subparsers.add_parser("random-combination", help="Get random component combination")
    random_combo.add_argument("--complexity", help="Filter by complexity")

    # Stats
    subparsers.add_parser("stats", help="Show knowledge base statistics")

    # Export
    export_cmd = subparsers.add_parser("export", help="Export knowledge base")
    export_cmd.add_argument("--output", required=True, help="Output file path")

    # Import
    import_cmd = subparsers.add_parser("import", help="Import knowledge base")
    import_cmd.add_argument("--input", required=True, help="Input file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    km = KnowledgeManager()

    if args.command == "list-evasion":
        results = km.list_evasion_techniques(args.type, args.complexity)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif args.command == "get-evasion":
        result = km.get_evasion_technique(args.id)
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"Technique {args.id} not found")

    elif args.command == "add-evasion":
        technique = {
            "name": args.name,
            "evasion_type": args.type,
            "description": args.description,
            "complexity": args.complexity,
            "detection_risk": args.detection_risk,
        }
        if args.code_template:
            technique["code_template"] = args.code_template
        if args.apis:
            technique["apis"] = [a.strip() for a in args.apis.split(",")]
        if args.references:
            technique["references"] = [r.strip() for r in args.references.split(",")]

        tech_id = km.add_evasion_technique(technique)
        print(f"Added evasion technique: {tech_id}")

    elif args.command == "get-components":
        results = km.get_components(args.type)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif args.command == "add-component":
        component = {
            "name": args.name,
            "description": args.description,
            "complexity": args.complexity,
        }
        if args.apis:
            component["apis"] = [a.strip() for a in args.apis.split(",")]
        if args.references:
            component["references"] = [r.strip() for r in args.references.split(",")]

        comp_id = km.add_component(args.type, component)
        print(f"Added component: {comp_id}")

    elif args.command == "list-scenarios":
        results = km.list_scenarios(args.status)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif args.command == "add-scenario":
        scenario_id = km.add_scenario(
            name=args.name,
            storage=args.storage,
            allocator=args.allocator,
            copier=args.copier,
            executor=args.executor,
            status=args.status
        )
        print(f"Added scenario: {scenario_id}")

    elif args.command == "update-scenario":
        notes = [args.notes] if args.notes else None
        success = km.update_scenario(
            scenario_id=args.id,
            status=args.status,
            loader_id=args.loader_id,
            notes=notes
        )
        if success:
            print(f"Updated scenario: {args.id}")
        else:
            print(f"Scenario {args.id} not found")

    elif args.command == "add-loader-technique":
        tech_id = km.add_loader_technique(
            storage=args.storage,
            allocator=args.allocator,
            copier=args.copier,
            executor=args.executor
        )
        print(f"Added loader technique: {tech_id}")

    elif args.command == "random-combination":
        result = km.random_combination(args.complexity)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "stats":
        stats = km.get_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))

    elif args.command == "export":
        km.export_knowledge(args.output)
        print(f"Exported to: {args.output}")

    elif args.command == "import":
        km.import_knowledge(args.input)
        print(f"Imported from: {args.input}")


if __name__ == "__main__":
    main()
