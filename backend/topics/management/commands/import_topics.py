import json
import re
from pathlib import Path

from django.core.management.base import BaseCommand

from topics.models import Category, Topic


CATEGORIES = [
    ("django", "Django", 0),
    ("docker", "Docker", 1),
    ("git", "Git", 2),
    ("http-api", "HTTP / API", 3),
    ("python", "Python", 4),
    ("tools-devops-linux", "Tools / DevOps / Linux", 5),
    ("algorithms", "Алгоритми", 6),
    ("architecture", "Архітектура", 7),
    ("async", "Асинхронність", 8),
    ("databases", "Бази даних", 9),
    ("oop", "ООП", 10),
    ("dev-processes", "Розробка та процеси", 11),
    ("testing", "Тестування", 12),
]

# Map category name (from .md "Category: X") to slug
CATEGORY_NAME_TO_SLUG = {name: slug for slug, name, _ in CATEGORIES}
# Variant spelling in some .md files
CATEGORY_NAME_TO_SLUG["Tools / Devops / Linux"] = "tools-devops-linux"

SHORT_ANSWER_HEADING = "### 1️⃣ Як коротко відповісти"
DETAILED_HEADING = "### 2️⃣ Детальне пояснення теми"
ID_PATTERN = re.compile(r"- ID: `(\d+)`")
INDEX_PATTERN = re.compile(r"- Index: `(\d+)`")
URL_PATTERN = re.compile(r"- URL: (.+)")
CATEGORY_PATTERN = re.compile(r"- Category:\s*(.+)")


def parse_md_file(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines:
        return None
    title = lines[0].strip()
    if title.startswith("# "):
        title = title[2:].strip()
    id_match = None
    index_val = 0
    url_val = ""
    category_name = ""
    for line in lines[1:15]:
        id_m = ID_PATTERN.search(line)
        if id_m:
            id_match = int(id_m.group(1))
        idx_m = INDEX_PATTERN.search(line)
        if idx_m:
            index_val = int(idx_m.group(1))
        url_m = URL_PATTERN.search(line)
        if url_m:
            url_val = url_m.group(1).strip()
        cat_m = CATEGORY_PATTERN.search(line)
        if cat_m:
            category_name = cat_m.group(1).strip()
    if id_match is None:
        return None
    question_id = id_match
    slug = CATEGORY_NAME_TO_SLUG.get(category_name) if category_name else None
    short_answer = ""
    detailed_explanation = ""
    if SHORT_ANSWER_HEADING in text:
        parts = text.split(SHORT_ANSWER_HEADING, 1)
        if DETAILED_HEADING in parts[1]:
            short_block, rest = parts[1].split(DETAILED_HEADING, 1)
            short_answer = short_block.strip()
            detailed_explanation = rest.strip()
        else:
            short_answer = parts[1].strip()
    else:
        if DETAILED_HEADING in text:
            _, detailed_explanation = text.split(DETAILED_HEADING, 1)
            detailed_explanation = detailed_explanation.strip()
    return {
        "question_id": question_id,
        "index": index_val,
        "title": title,
        "source_url": url_val,
        "short_answer": short_answer,
        "detailed_explanation": detailed_explanation,
        "raw_markdown": text,
        "category_slug": slug,
    }


class Command(BaseCommand):
    help = "Import topics from markdown files and category mapping JSON."

    def add_arguments(self, parser):
        parser.add_argument(
            "--data-dir",
            type=Path,
            required=True,
            help="Path to directory with NNNN_qID.md files",
        )
        parser.add_argument(
            "--mapping",
            type=Path,
            required=False,
            default=None,
            help="Optional: path to category_mapping.json (question_id -> slug) for files without Category in .md",
        )

    def handle(self, *args, **options):
        data_dir: Path = options["data_dir"].resolve()
        mapping_path: Path | None = options.get("mapping")
        mapping = {}
        if mapping_path:
            mapping_path = mapping_path.resolve()
            if not mapping_path.is_file():
                self.stderr.write(self.style.ERROR(f"Mapping file not found: {mapping_path}"))
                return
            mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
            mapping = {str(k): str(v).strip().lower() for k, v in mapping.items()}
        if not data_dir.is_dir():
            self.stderr.write(self.style.ERROR(f"Not a directory: {data_dir}"))
            return
        slug_to_category = {}
        for slug, name, order in CATEGORIES:
            cat, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "order": order},
            )
            slug_to_category[slug] = cat
        md_files = sorted(data_dir.glob("*.md"))
        created = 0
        updated = 0
        skipped = 0
        for md_path in md_files:
            name = md_path.stem
            if not re.match(r"^\d{4}_q\d+$", name):
                skipped += 1
                continue
            parsed = parse_md_file(md_path)
            if not parsed:
                skipped += 1
                continue
            qid = parsed["question_id"]
            slug = parsed.get("category_slug") or mapping.get(str(qid))
            if not slug or slug not in slug_to_category:
                self.stdout.write(
                    self.style.WARNING(
                        f"No category for question_id={qid} ({md_path.name}): "
                        f"add 'Category: ...' in .md or use --mapping"
                    )
                )
                skipped += 1
                continue
            category = slug_to_category[slug]
            _, was_created = Topic.objects.update_or_create(
                question_id=qid,
                defaults={
                    "category": category,
                    "title": parsed["title"],
                    "index": parsed["index"],
                    "source_url": parsed["source_url"] or "",
                    "short_answer": parsed["short_answer"],
                    "detailed_explanation": parsed["detailed_explanation"],
                    "raw_markdown": parsed["raw_markdown"],
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Done: {created} created, {updated} updated, {skipped} skipped."
            )
        )
