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