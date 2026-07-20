#!/usr/bin/env python3
"""DB A 向量知识库 - 查询脚本

用法:
  python shared/scripts/query_db_a.py --query "transformer attention" --top_k 10
  python shared/scripts/query_db_a.py --list-all
"""
import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DB_A_DIR = PROJECT_ROOT / "shared" / "db_a"


def main():
    parser = argparse.ArgumentParser(description="DB A 知识库查询")
    parser.add_argument("--query", default="", help="查询文本")
    parser.add_argument("--top_k", type=int, default=10, help="返回结果数")
    parser.add_argument("--list-all", action="store_true", help="列出所有记录")

    args = parser.parse_args()

    if not args.query and not args.list_all:
        parser.print_help()
        return

    try:
        import pickle
        store_path = DB_A_DIR / "paper_knowledge.pkl"
        if not store_path.exists():
            print("❌ 知识库为空（文件不存在），请先使用 store_to_db_a.py 入库")
            return

        with open(store_path, "rb") as f:
            data = pickle.load(f)
        records = data.get("records", [])

        if args.list_all:
            print(f"📊 知识库共 {len(records)} 条记录:\n")
            for i, r in enumerate(records, 1):
                print(f"{i}. [{r['paper_id']}] {r['title']}")
                print(f"   主题: {', '.join(r['related_topics'][:3])}")
                print(f"   tags: {', '.join(r['tags'][:3])}")
                print()
            return

        # 简单关键词匹配（实际场景用向量检索，这里做关键词匹配兜底）
        query = args.query.lower()
        scored = []
        for r in records:
            score = 0
            text = (r["title"] + " " + r["summary"] + " " + r["content"]).lower()
            for kw in query.split():
                if kw in text:
                    score += text.count(kw)
            if score > 0:
                scored.append((score, r))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = scored[:args.top_k]

        if not results:
            print(f"⚠️ 未找到与 '{args.query}' 相关的记录")
            return

        print(f"🔍 查询: '{args.query}' → 找到 {len(results)} 条结果:\n")
        for i, (score, r) in enumerate(results, 1):
            print(f"{i}. [{r['paper_id']}] {r['title']}  [匹配度:{score}]")
            print(f"   摘要: {r['summary'][:150]}")
            print(f"   主题: {', '.join(r['related_topics'][:3])}")
            print()

    except Exception as e:
        print(f"❌ 查询失败: {e}")


if __name__ == "__main__":
    main()
