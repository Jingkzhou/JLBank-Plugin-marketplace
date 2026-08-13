from __future__ import annotations

import json


def test_discovers_subagent_transcripts_by_parent_tool_use_id(
    hook_module,
    fixture_transcript_path,
):
    transcript = fixture_transcript_path("async_agent_completed")

    subagents = hook_module.get_subagent_transcripts_by_tool_use_id(transcript)

    assert set(subagents) == {"toolu_agent_complete"}
    subagent = subagents["toolu_agent_complete"]
    assert subagent["agent_id"] == "agent-complete"
    assert subagent["agent_type"] == "general-purpose"
    assert subagent["description"] == "Summarize docs"
    assert subagent["path"].name == "agent-agent-complete.jsonl"


def test_discovers_nested_subagent_metadata_seen_in_real_claude_code_transcripts(
    hook_module,
    fixture_transcript_path,
):
    transcript = fixture_transcript_path("nested_subagents")

    subagents = hook_module.get_subagent_transcripts_by_tool_use_id(transcript)

    assert set(subagents) == {"toolu_outer_agent", "toolu_inner_agent"}
    assert subagents["toolu_outer_agent"]["agent_id"] == "outer-agent"
    assert subagents["toolu_inner_agent"]["agent_id"] == "inner-agent"
    assert subagents["toolu_inner_agent"]["agent_type"] == "fork"


def test_discovers_workflow_agent_transcripts_by_run_id(hook_module, fixture_transcript_path):
    transcript = fixture_transcript_path("workflow_subagents")

    workflows = hook_module.get_workflow_agent_transcripts_by_run_id(transcript)

    assert set(workflows) == {"wf_test001"}
    agents = workflows["wf_test001"]
    # The journal also holds a started-row for "r3" with no result and no
    # meta/jsonl on disk (real partial-journal case: agent still running or
    # torn down early) — discovery is meta-driven, so r3 never surfaces.
    assert [agent["agent_id"] for agent in agents] == ["r1", "r2"]
    assert [agent["path"].name for agent in agents] == ["agent-r1.jsonl", "agent-r2.jsonl"]
    assert all(agent["agent_type"] == "workflow-subagent" for agent in agents)
    # Per-agent return values come from the run's journal.jsonl.
    assert agents[0]["result"] == {"verdict": "claim A holds", "confidence": "high"}
    assert agents[1]["result"] == {"verdict": "claim B holds", "confidence": "high"}


def test_workflow_agents_stay_invisible_to_classic_subagent_discovery(
    hook_module,
    fixture_transcript_path,
):
    # Documented split: the classic function keys strictly by toolUseId and
    # stays non-recursive; workflow agents are only reachable via the new map.
    transcript = fixture_transcript_path("workflow_subagents")

    assert hook_module.get_subagent_transcripts_by_tool_use_id(transcript) == {}


def test_workflow_discovery_ignores_bad_or_foreign_metadata(hook_module, tmp_path):
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text("", encoding="utf-8")
    run_dir = tmp_path / "transcript" / "subagents" / "workflows" / "wf_x1"
    run_dir.mkdir(parents=True)
    (run_dir / "agent-bad.meta.json").write_text("{not-json", encoding="utf-8")
    (run_dir / "agent-classic.meta.json").write_text(
        json.dumps({"agentType": "general-purpose", "toolUseId": "toolu_x"}),
        encoding="utf-8",
    )
    (run_dir / "agent-classic.jsonl").write_text("", encoding="utf-8")
    (run_dir / "agent-no-jsonl.meta.json").write_text(
        json.dumps({"agentType": "workflow-subagent", "spawnDepth": 1}),
        encoding="utf-8",
    )

    assert hook_module.get_workflow_agent_transcripts_by_run_id(transcript) == {}


def test_workflow_discovery_drops_run_dirs_with_journal_but_no_agents(hook_module, tmp_path):
    # A run dir can exist with only its journal (e.g. the workflow crashed
    # before spawning agents, or agents were cleaned up): no agent metas means
    # nothing to emit, so the run must not surface at all.
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text("", encoding="utf-8")
    run_dir = tmp_path / "transcript" / "subagents" / "workflows" / "wf_journal_only"
    run_dir.mkdir(parents=True)
    (run_dir / "journal.jsonl").write_text(
        json.dumps({"type": "started", "key": "v2:abc", "agentId": "r1"}) + "\n",
        encoding="utf-8",
    )

    assert hook_module.get_workflow_agent_transcripts_by_run_id(transcript) == {}


def test_workflow_discovery_ignores_orphan_agent_jsonl_without_meta(hook_module, tmp_path):
    # Discovery is meta-driven: an agent transcript without its meta.json
    # (half-written run, partial cleanup) stays invisible instead of crashing
    # or emitting an unidentifiable agent.
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text("", encoding="utf-8")
    run_dir = tmp_path / "transcript" / "subagents" / "workflows" / "wf_orphan"
    run_dir.mkdir(parents=True)
    (run_dir / "agent-orphan.jsonl").write_text(
        json.dumps({"type": "user", "message": {"role": "user", "content": "hi"}}) + "\n",
        encoding="utf-8",
    )

    assert hook_module.get_workflow_agent_transcripts_by_run_id(transcript) == {}


def test_workflow_discovery_accepts_metas_with_extra_real_world_keys(hook_module, tmp_path):
    # Harvested ground truth: real metas carry only agentType/spawnDepth, plus
    # worktreePath when the run launched from a worktree (key order
    # agentType -> worktreePath -> spawnDepth, matching the real meta).
    # "model" is NOT harvested from any real meta — it is a hypothetical extra
    # key probing that discovery keys on agentType only and tolerates unknown
    # additions.
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text("", encoding="utf-8")
    run_dir = tmp_path / "transcript" / "subagents" / "workflows" / "wf_x3"
    run_dir.mkdir(parents=True)
    (run_dir / "agent-a1.meta.json").write_text(
        json.dumps({
            "agentType": "workflow-subagent",
            "worktreePath": "/repo/.claude/worktrees/wf_x3-11",
            "spawnDepth": 1,
            "model": "claude-test",
        }),
        encoding="utf-8",
    )
    (run_dir / "agent-a1.jsonl").write_text("", encoding="utf-8")

    workflows = hook_module.get_workflow_agent_transcripts_by_run_id(transcript)

    assert set(workflows) == {"wf_x3"}
    assert workflows["wf_x3"][0]["agent_id"] == "a1"
    assert workflows["wf_x3"][0]["agent_type"] == "workflow-subagent"


def test_workflow_discovery_without_journal_leaves_results_empty(hook_module, tmp_path):
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text("", encoding="utf-8")
    run_dir = tmp_path / "transcript" / "subagents" / "workflows" / "wf_x2"
    run_dir.mkdir(parents=True)
    (run_dir / "agent-a1.meta.json").write_text(
        json.dumps({"agentType": "workflow-subagent", "spawnDepth": 1}),
        encoding="utf-8",
    )
    (run_dir / "agent-a1.jsonl").write_text("", encoding="utf-8")

    workflows = hook_module.get_workflow_agent_transcripts_by_run_id(transcript)

    assert set(workflows) == {"wf_x2"}
    assert workflows["wf_x2"][0]["agent_id"] == "a1"
    assert workflows["wf_x2"][0]["result"] is None


def test_ignores_bad_or_incomplete_subagent_metadata(hook_module, tmp_path):
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text("", encoding="utf-8")
    subagent_dir = tmp_path / "transcript" / "subagents"
    subagent_dir.mkdir(parents=True)
    (subagent_dir / "agent-bad.meta.json").write_text("{not-json", encoding="utf-8")
    (subagent_dir / "agent-missing-jsonl.meta.json").write_text(
        json.dumps({"toolUseId": "toolu_missing"}),
        encoding="utf-8",
    )
    (subagent_dir / "agent-missing-tool-id.meta.json").write_text(
        json.dumps({"description": "No tool id"}),
        encoding="utf-8",
    )
    (subagent_dir / "agent-missing-tool-id.jsonl").write_text("", encoding="utf-8")

    assert hook_module.get_subagent_transcripts_by_tool_use_id(transcript) == {}
