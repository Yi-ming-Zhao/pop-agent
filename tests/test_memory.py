from pop_agent.memory import MemoryStore, MemoryUpdate


def test_memory_update_and_search(tmp_path):
    store = MemoryStore(tmp_path)
    written = store.apply_updates(
        "alice",
        [
            MemoryUpdate(
                section="knowledge",
                title="黑洞基础",
                summary="用户知道黑洞和强引力有关，但不熟悉事件视界。",
                tags=["黑洞", "事件视界"],
                confidence=0.8,
                source_run="run_test",
            )
        ],
    )

    assert written == ["knowledge: 黑洞基础"]
    results = store.search("alice", "黑洞 事件视界")
    assert results
    assert results[0].title == "黑洞基础"
    assert results[0].confidence == 0.8


def test_memory_show_initializes_files(tmp_path):
    store = MemoryStore(tmp_path)
    content = store.show("bob")
    assert "用户认知画像" in content
    assert (tmp_path / "memory" / "users" / "bob" / "profile.md").exists()
