import unittest

from data_loader import DataLoader


class QueryContextTests(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader(data_dir="")
        self.loader.chunks = [
            {
                "code": "T01-001",
                "section": "Product management",
                "text": "Product manager tập trung vào vấn đề và nhu cầu người dùng.",
                "source": "transcript-01-clean.md",
            },
            {
                "code": "T06-086",
                "section": "Self-attention",
                "text": "Self-attention tính mức độ liên quan giữa các token trong ngữ cảnh.",
                "source": "transcript-06-clean.md",
            },
            {
                "code": "T05-017",
                "section": "Workflow",
                "text": "Workflow là chuỗi các bước chuyển đổi đầu vào thành đầu ra.",
                "source": "transcript-05-clean.md",
            },
        ]
        self.loader._build_search_index()

    def test_custom_question_retrieves_late_corpus_topic(self):
        context = self.loader.get_context_for_query(
            "Self-attention hoạt động như thế nào?"
        )

        self.assertIn("[T06-086]", context)
        self.assertNotIn("[T01-001]", context)

    def test_different_custom_question_gets_different_context(self):
        context = self.loader.get_context_for_query(
            "Workflow gồm những bước chuyển đổi nào?"
        )

        self.assertIn("[T05-017]", context)
        self.assertNotIn("[T06-086]", context)


if __name__ == "__main__":
    unittest.main()
