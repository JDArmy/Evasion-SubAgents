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

    def find_similar_techniques(self, technique: dict) -> list:
        """
        Find techniques that might be similar (for AI/human review).

        Returns list of similar techniques with similarity info.
        Does NOT decide if duplicate - just finds candidates for review.
        """
        data = self._load_json("evasion")
        similar = []

        name = technique.get("name", "").lower().strip()
        desc = technique.get("description", "").lower()
        ttype = technique.get("type", technique.get("evasion_type", ""))
        apis = set(technique.get("apis", []))
        keywords = self._extract_keywords(name + " " + desc)

        for existing in data["techniques"]:
            existing_name = existing.get("name", "").lower().strip()
            existing_desc = existing.get("description", "").lower()
            existing_type = existing.get("type", existing.get("evasion_type", ""))
            existing_apis = set(existing.get("apis", []))
            existing_keywords = self._extract_keywords(existing_name + " " + existing_desc)

            similarity_score = 0
            similarity_reasons = []

            # 1. Exact name match (definite duplicate candidate)
            if name == existing_name:
                similar.append({
                    "technique": existing,
                    "similarity_score": 100,
                    "reasons": ["Exact name match"],
                    "match_type": "exact_name"
                })
                continue

            # 2. Same type
            if ttype and ttype == existing_type:
                similarity_score += 20
                similarity_reasons.append(f"Same type: {ttype}")

            # 3. Name similarity
            name_similarity = self._calculate_similarity(name, existing_name)
            if name_similarity > 0.5:
                similarity_score += int(name_similarity * 40)
                similarity_reasons.append(f"Name similarity: {name_similarity:.0%}")

            # 4. Keyword overlap
            if keywords and existing_keywords:
                keyword_overlap = len(keywords & existing_keywords) / max(len(keywords), len(existing_keywords))
                if keyword_overlap > 0.3:
                    similarity_score += int(keyword_overlap * 30)
                    shared = keywords & existing_keywords
                    if shared:
                        similarity_reasons.append(f"Shared keywords: {', '.join(list(shared)[:5])}")

            # 5. API overlap
            if apis and existing_apis:
                api_overlap = len(apis & existing_apis) / max(len(apis), len(existing_apis))
                if api_overlap > 0.5:
                    similarity_score += int(api_overlap * 30)
                    shared_apis = apis & existing_apis
                    similarity_reasons.append(f"Shared APIs: {', '.join(list(shared_apis)[:3])}")

            # 6. Source overlap
            source = technique.get("source", "")
            existing_source = existing.get("source", "")
            if source and existing_source and source == existing_source:
                similarity_score += 10
                similarity_reasons.append(f"Same source: {source}")

            if similarity_score >= 30:
                similar.append({
                    "technique": existing,
                    "similarity_score": similarity_score,
                    "reasons": similarity_reasons,
                    "match_type": "similar" if similarity_score >= 50 else "related"
                })

        # Sort by similarity score
        similar.sort(key=lambda x: x["similarity_score"], reverse=True)
        return similar

    def _extract_keywords(self, text: str) -> set:
        """Extract important keywords from text"""
        # Common words to ignore
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will", "would",
            "could", "should", "may", "might", "must", "shall", "can", "need",
            "this", "that", "these", "those", "it", "its", "as", "if", "when",
            "than", "so", "no", "not", "only", "own", "same", "than", "too",
            "very", "just", "also", "now", "here", "there", "where", "which",
            "who", "whom", "what", "how", "why", "all", "each", "every", "both",
            "few", "more", "most", "other", "some", "such", "any", "into", "through"
        }

        # Important security terms (lower weight but meaningful)
        security_terms = {
            "syscall", "hook", "inject", "bypass", "evade", "obfuscate",
            "encrypt", "decrypt", "shellcode", "loader", "memory", "process",
            "thread", "api", "ntdll", "kernel", "user", "peb", "teb", "amsi",
            "etw", "edr", "av", "antivirus", "debug", "sandbox", "vm", "virtual"
        }

        words = text.lower().split()
        keywords = set()

        for word in words:
            word = word.strip(".,!?;:\"'()[]{}")
            if len(word) >= 3 and word not in stop_words:
                keywords.add(word)

        return keywords

    def format_comparison_for_ai(self, new_technique: dict, similar_techniques: list) -> str:
        """Format comparison for AI analysis"""
        output = []
        output.append("=" * 60)
        output.append("NEW TECHNIQUE TO ADD:")
        output.append("=" * 60)
        output.append(f"Name: {new_technique.get('name')}")
        output.append(f"Type: {new_technique.get('type', new_technique.get('evasion_type'))}")
        output.append(f"Description: {new_technique.get('description')}")
        output.append(f"Complexity: {new_technique.get('complexity')}")
        output.append(f"Detection Risk: {new_technique.get('detection_risk')}")
        if new_technique.get('apis'):
            output.append(f"APIs: {', '.join(new_technique.get('apis', []))}")
        output.append(f"Source: {new_technique.get('source', 'unknown')}")
        output.append("")

        if not similar_techniques:
            output.append("No similar techniques found in knowledge base.")
            output.append("RECOMMENDATION: ADD (no duplicates detected)")
        else:
            output.append("=" * 60)
            output.append(f"SIMILAR TECHNIQUES FOUND ({len(similar_techniques)}):")
            output.append("=" * 60)

            for i, item in enumerate(similar_techniques, 1):
                t = item["technique"]
                output.append(f"\n--- [{i}] {t['id']}: {t['name']} (Score: {item['similarity_score']}) ---")
                output.append(f"Type: {t.get('type', t.get('evasion_type'))}")
                output.append(f"Description: {t.get('description')}")
                output.append(f"Complexity: {t.get('complexity')}")
                output.append(f"Detection Risk: {t.get('detection_risk')}")
                if t.get('apis'):
                    output.append(f"APIs: {', '.join(t.get('apis', []))}")
                output.append(f"Match Reasons: {', '.join(item['reasons'])}")
                output.append(f"Match Type: {item['match_type']}")

            output.append("\n" + "=" * 60)
            output.append("AI ANALYSIS REQUESTED:")
            output.append("=" * 60)
            output.append("Please analyze and determine if the new technique is:")
            output.append("  1. DUPLICATE - Same technique, should skip")
            output.append("  2. VARIATION - Same goal but different implementation, keep both")
            output.append("  3. DIFFERENT - Different technique entirely, add")
            output.append("")
            output.append("Consider:")
            output.append("  - Is the core technique the same or different?")
            output.append("  - Does it achieve the same goal in a different way?")
            output.append("  - Would a defender need different detection methods?")
            output.append("  - Is the complexity/detection risk meaningfully different?")

        return "\n".join(output)

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity using simple word overlap"""
        words1 = set(str1.split())
        words2 = set(str2.split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _check_duplicate_evasion(self, technique: dict) -> dict:
        """
        Check if technique is a duplicate or needs review.

        Returns dict with:
            - is_duplicate: bool
            - is_similar: bool
            - action: str (add, review, skip)
            - reason: str
            - existing_id: str (if duplicate/similar)
        """
        similar = self.find_similar_techniques(technique)

        for item in similar:
            if item.get("match_type") == "exact_name" and item.get("similarity_score", 0) >= 100:
                return {
                    "is_duplicate": True,
                    "is_similar": True,
                    "action": "skip",
                    "reason": f"Exact name match with existing technique",
                    "existing_id": item["technique"]["id"]
                }

        # Check for high similarity (likely duplicate)
        for item in similar:
            if item.get("similarity_score", 0) >= 70:
                return {
                    "is_duplicate": False,
                    "is_similar": True,
                    "action": "review",
                    "reason": f"Similar to existing technique (score: {item['similarity_score']})",
                    "existing_id": item["technique"]["id"]
                }

        return {
            "is_duplicate": False,
            "is_similar": False,
            "action": "add",
            "reason": "No duplicates found",
            "existing_id": None
        }

    def check_duplicate(self, name: str = None, technique_id: str = None) -> dict:
        """Check if a technique is duplicate (by name or ID)"""
        data = self._load_json("evasion")

        if technique_id:
            for t in data["techniques"]:
                if t.get("id") == technique_id:
                    return {"exists": True, "technique": t}
            return {"exists": False}

        if name:
            name_lower = name.lower().strip()
            for t in data["techniques"]:
                if t.get("name", "").lower().strip() == name_lower:
                    return {"exists": True, "technique": t}
            return {"exists": False}

        return {"exists": False}

    def add_evasion_technique(self, technique: dict, check_dup: bool = True) -> dict:
        """
        Add new evasion technique with deduplication.

        Args:
            technique: Technique dict to add
            check_dup: Whether to check for duplicates (default True)

        Returns:
            dict with keys:
                - success: bool
                - id: str (if added)
                - action: str (added, skipped, needs_review)
                - reason: str
        """
        # Check for duplicates
        if check_dup:
            dup_check = self._check_duplicate_evasion(technique)

            if dup_check["is_duplicate"]:
                return {
                    "success": False,
                    "action": "skipped",
                    "reason": dup_check["reason"],
                    "existing_id": dup_check["existing_id"]
                }

            if dup_check["is_similar"] and dup_check["action"] == "review":
                return {
                    "success": False,
                    "action": "needs_review",
                    "reason": dup_check["reason"],
                    "existing_id": dup_check["existing_id"],
                    "technique": technique
                }

        # Add the technique
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

        return {
            "success": True,
            "action": "added",
            "id": technique["id"],
            "reason": f"Successfully added as {technique['id']}"
        }

    def add_evasion_technique_legacy(self, technique: dict) -> str:
        """Legacy method for backward compatibility"""
        result = self.add_evasion_technique(technique, check_dup=False)
        return result.get("id", "")

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
    add_evasion.add_argument("--force", action="store_true", help="Skip duplicate check")

    # Check duplicate
    check_dup = subparsers.add_parser("check-duplicate", help="Check if technique is duplicate")
    check_dup.add_argument("--name", help="Technique name to check")
    check_dup.add_argument("--id", help="Technique ID to check")

    # Find similar
    find_similar = subparsers.add_parser("find-similar", help="Find similar techniques")
    find_similar.add_argument("--name", help="Technique name to check")
    find_similar.add_argument("--type", help="Filter by evasion type")
    find_similar.add_argument("--description", help="Technique description")
    find_similar.add_argument("--format-ai", action="store_true", help="Format output for AI analysis")

    # Dedup check (for AI review)
    dedup_check = subparsers.add_parser("dedup-check", help="Check for duplicates with AI-friendly output")
    dedup_check.add_argument("--name", required=True, help="Technique name")
    dedup_check.add_argument("--type", required=True, help="Technique type")
    dedup_check.add_argument("--description", required=True, help="Technique description")
    dedup_check.add_argument("--apis", help="Comma-separated API list")
    dedup_check.add_argument("--source", help="Technique source")

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
            "type": args.type,
            "evasion_type": args.type,  # Keep both for compatibility
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

        result = km.add_evasion_technique(technique, check_dup=not args.force)

        if result["success"]:
            print(f"[+] Added evasion technique: {result['id']}")
        else:
            action = result.get("action", "unknown")
            if action == "skipped":
                print(f"[SKIP] Skipped (duplicate): {result['reason']}")
            elif action == "needs_review":
                print(f"[REVIEW] Needs review: {result['reason']}")
                print(f"   Existing: {result.get('existing_id')}")
            else:
                print(f"[ERROR] Failed: {result.get('reason', 'Unknown error')}")

    elif args.command == "check-duplicate":
        result = km.check_duplicate(name=args.name, technique_id=args.id)
        if result["exists"]:
            print(f"Found: {result['technique']['id']} - {result['technique']['name']}")
            print(json.dumps(result["technique"], indent=2, ensure_ascii=False))
        else:
            print("No duplicate found")

    elif args.command == "find-similar":
        technique = {
            "name": args.name or "",
            "type": args.type or "",
            "description": args.description or "",
            "apis": []
        }
        similar = km.find_similar_techniques(technique)

        if args.format_ai:
            print(km.format_comparison_for_ai(technique, similar))
        else:
            if similar:
                print(f"Found {len(similar)} similar technique(s):")
                for item in similar:
                    t = item["technique"]
                    print(f"\n  {t['id']}: {t['name']} (Score: {item['similarity_score']})")
                    print(f"    Type: {t.get('type', t.get('evasion_type'))}")
                    print(f"    Reasons: {', '.join(item['reasons'])}")
            else:
                print("No similar techniques found")

    elif args.command == "dedup-check":
        technique = {
            "name": args.name,
            "type": args.type,
            "evasion_type": args.type,
            "description": args.description,
            "apis": [a.strip() for a in args.apis.split(",")] if args.apis else [],
            "source": args.source or "unknown"
        }
        similar = km.find_similar_techniques(technique)
        print(km.format_comparison_for_ai(technique, similar))

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
