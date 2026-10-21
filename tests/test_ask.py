import sys
from types import SimpleNamespace

from app import ask


class FakeChat:
    def __init__(self):
        self.questions = []

    def send_message(self, question):
        self.questions.append(question)
        return SimpleNamespace(
            text=f"回答: {question}",
            usage_metadata=SimpleNamespace(
                prompt_token_count=3,
                candidates_token_count=5,
            ),
        )


def test_main_keeps_one_chat_for_follow_up_questions(monkeypatch, capsys):
    chat = FakeChat()
    chats = SimpleNamespace(create=lambda *, model: chat)
    client = SimpleNamespace(chats=chats)
    monkeypatch.setattr(ask.genai, "Client", lambda *, api_key: client)
    monkeypatch.setattr(ask, "get_api_key", lambda: "test-key")
    questions = iter(["追加質問", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(questions))
    monkeypatch.setattr(sys, "argv", ["app.ask", "最初の質問"])
    monkeypatch.setattr(ask, "MODEL", "test-model")

    ask.main()

    output = capsys.readouterr().out
    assert chat.questions == ["最初の質問", "追加質問"]
    assert output.count("[トークン数]") == 2
    assert "回答: 追加質問" in output
