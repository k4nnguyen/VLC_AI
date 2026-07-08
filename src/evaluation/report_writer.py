import json
import csv
from pathlib import Path


class ReportWriter:
    def __init__(self, output_dir="src/evaluation/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    def save(self, report: dict, method: str):
        self._save_json(report, method)
        self._save_csv(report, method)

    def save_comparison(self, comparison: dict, method: str = "comparison"):
        self._save_comparison_json(comparison, method)
        self._save_comparison_csv(comparison, method)

    def save_generation(self, report: dict, method: str = "generation"):
        self._save_json(report, method)
        self._save_generation_csv(report, method)

    def _save_json(self, report, method):
        path = self.output_dir / f"{method}.json"
        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                report,
                f,
                ensure_ascii=False,
                indent=4
            )
            
    def _save_csv(self, report, method):
        path = self.output_dir / f"{method}.csv"
        with open(
            path,
            "w",
            newline="",
            encoding="utf-8"
        ) as f:
            writer = csv.writer(f)
            writer.writerow([
                "question",
                "expected",
                "retrieved",
                "hit",
                "rank",
                "recall",
                "precision"
            ])
            for item in report["details"]:
                writer.writerow([
                    item["question"],
                    ",".join(map(str, item["expected"])),
                    ",".join(map(str, item["retrieved"])),
                    item["hit"],
                    item["rank"],
                    item["recall"],
                    item["precision"]
                ])

    def _save_comparison_json(self, comparison, method):
        path = self.output_dir / f"{method}.json"
        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                comparison,
                f,
                ensure_ascii=False,
                indent=4
            )

    def _save_comparison_csv(self, comparison, method):
        path = self.output_dir / f"{method}.csv"
        with open(
            path,
            "w",
            newline="",
            encoding="utf-8"
        ) as f:
            writer = csv.writer(f)
            if method == "query_rewrite_comparison":
                writer.writerow([
                    "group",
                    "index",
                    "category",
                    "question",
                    "rewritten_question",
                    "baseline_hit",
                    "rewritten_hit",
                    "expected"
                ])
                for group_name, items in comparison["groups"].items():
                    for item in items:
                        writer.writerow([
                            group_name,
                            item["index"],
                            item.get("category", ""),
                            item["question"],
                            item.get("rewritten_question", ""),
                            item.get("baseline_hit", ""),
                            item.get("hit", ""),
                            ",".join(map(str, item["expected"]))
                        ])
            else:
                writer.writerow([
                    "group",
                    "index",
                    "category",
                    "question",
                    "embedding_hit",
                    "bm25_hit",
                    "expected"
                ])
                for group_name, items in comparison["groups"].items():
                    for item in items:
                        writer.writerow([
                            group_name,
                            item["index"],
                            item.get("category", ""),
                            item["question"],
                            item.get("embedding_hit", ""),
                            item.get("bm25_hit", ""),
                            ",".join(map(str, item["expected"]))
                        ])

    def _save_generation_csv(self, report, method):
        path = self.output_dir / f"{method}.csv"
        with open(
            path,
            "w",
            newline="",
            encoding="utf-8"
        ) as f:
            writer = csv.writer(f)
            writer.writerow([
                "question",
                "reference_answer",
                "answer",
                "verified_citations",
            ])
            for item in report["details"]:
                writer.writerow([
                    item["question"],
                    item.get("reference_answer", ""),
                    item.get("answer", ""),
                    ";".join(item.get("verified_citations", [])),
                ])