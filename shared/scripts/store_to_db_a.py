#!/usr/bin/env python3
"""DB A 向量知识库 - 入库脚本

用法:
  python shared/scripts/store_to_db_a.py --action add --paper_id "xxx" --title "xxx" --content "xxx"
  python shared/scripts/store_to_db_a.py --action list
  python shared/scripts/store_to_db_a.py --action clear
"""
import argparse
import json
import sys
from pathlib import Path

# 添加项目根到路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DB_A_DIR = PROJECT_ROOT / "shared" / "db_a"
KNOWLEDGE_MD_DIR = PROJECT_ROOT / "shared" / "knowledge_md"


def get_store():
    """懒加载向量库"""
    import pickle

    class SimpleVectorStore:
        def __init__(self, persist_dir):
            self.persist_dir = Path(persist_dir)
            self.persist_dir.mkdir(parents=True, exist_ok=True)
            self.store_path = self.persist_dir / "paper_knowledge.pkl"
            self.records = []
            self._load()

        def add(self, paper_id, title, content, summary="",
                contributions=None, topics=None, methods=None, tags=None):
            record = {
                "id": f"rec_{paper_id}",
                "paper_id": paper_id,
                "title": title,
                "content": content or f"{title}\u3002{summary}",
                "summary": summary,
                "main_contributions": contributions or [],
                "related_topics": topics or [],
                "methods_used": methods or [],
                "tags": tags or [],
                "source": "association_agent",
                "created_at": str(__import__("datetime").datetime.now()),
            }
            self.records.append(record)
            self._save()
            return record["id"]

        def list_all(self):
            return self.records

        def clear(self):
            self.records = []
            self._save()

        def count(self):
            return len(self.records)

        def _save(self):
            with open(self.store_path, "wb") as f:
                import pickle
                pickle.dump({"records": self.records}, f)

        def _load(self):
            if self.store_path.exists():
                import pickle
                with open(self.store_path, "rb") as f:
                    data = pickle.load(f)
                    self.records = data.get("records", [])

    return SimpleVectorStore(DB_A_DIR)


def main():
    parser = argparse.ArgumentParser(description="DB A 知识库操作")
    parser.add_argument("--action", required=True, choices=["add", "list", "clear", "count"])
    parser.add_argument("--paper_id", default="")
    parser.add_argument("--title", default="")
    parser.add_argument("--content", default="")
    parser.add_argument("--summary", default="")
    parser.add_argument("--contributions", default="")
    parser.add_argument("--topics", default="")
    parser.add_argument("--methods", default="")
    parser.add_argument("--tags", default="")

    args = parser.parse_args()
    store = get_store()

    if args.action == "add":
        pid = store.add(
            paper_id=args.paper_id,
            title=args.title,
            content=args.content,
            summary=args.summary,
            contributions=args.contributions.split("|") if args.contributions else [],
            topics=args.topics.split("|") if args.topics else [],
            methods=args.methods.split("|") if args.methods else [],
            tags=args.tags.split("|") if args.tags else [],
        )
        print(f"✅ 入库成功: {pid}")
        print(f"📊 知识库总量: {store.count()} 条")

        # 同步生成人类可读的 MD 文档（中文标题）
        KNOWLEDGE_MD_DIR.mkdir(parents=True, exist_ok=True)
        safe_title = (args.summary or args.title).replace("/", "-").replace(":", " -")
        md_path = KNOWLEDGE_MD_DIR / f"{safe_title}.md"
        import datetime
        md = f"""# {args.title}

> **入库时间**: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
> **论文ID**: {args.paper_id}
> **标签**: {args.tags}

---

## 摘要

{args.summary}

## 内容

{args.content}

## 主要贡献

"""
        for c in (args.contributions.split("|") if args.contributions else []):
            md += f"- {c}\n"
        md += f"""
## 相关主题

{args.topics}

## 使用方法

{args.methods}
"""
        md_path.write_text(md, encoding="utf-8")
        print(f"📄 人类可读文档已生成: knowledge_md/{md_path.name}")

    elif args.action == "list":
        records = store.list_all()
        print(f"📊 知识库共 {len(records)} 条记录:\n")
        for r in records:
            print(f"  [{r['paper_id']}] {r['title']}")
            print(f"    主题: {', '.join(r['related_topics'][:3])}")
            print()

    elif args.action == "clear":
        store.clear()
        print("✅ 知识库已清空")

    elif args.action == "count":
        print(f"📊 知识库总量: {store.count()} 条")


if __name__ == "__main__":
    main()
