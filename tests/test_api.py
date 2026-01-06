import pytest


class TestIdeasAPI:
    @pytest.mark.asyncio
    async def test_create_idea(self, client):
        # given: idea content
        data = {"content": "Test idea content"}
        
        # when: POST to create idea
        response = await client.post("/api/ideas", json=data)
        
        # then: idea is created with draft status
        assert response.status_code == 201
        result = response.json()
        assert result["content"] == "Test idea content"
        assert result["status"] == "draft"
        assert result["id"] is not None

    @pytest.mark.asyncio
    async def test_list_ideas(self, client):
        # given: multiple ideas exist
        await client.post("/api/ideas", json={"content": "Idea 1"})
        await client.post("/api/ideas", json={"content": "Idea 2"})
        
        # when: GET all ideas
        response = await client.get("/api/ideas")
        
        # then: all ideas are returned
        assert response.status_code == 200
        ideas = response.json()
        assert len(ideas) == 2

    @pytest.mark.asyncio
    async def test_get_idea_with_messages(self, client):
        # given: an idea exists
        create_response = await client.post("/api/ideas", json={"content": "Test idea"})
        idea_id = create_response.json()["id"]
        
        # when: GET single idea
        response = await client.get(f"/api/ideas/{idea_id}")
        
        # then: idea with messages is returned
        assert response.status_code == 200
        result = response.json()
        assert result["id"] == idea_id
        assert "messages" in result

    @pytest.mark.asyncio
    async def test_update_idea(self, client):
        # given: an idea exists
        create_response = await client.post("/api/ideas", json={"content": "Original content"})
        idea_id = create_response.json()["id"]
        
        # when: PUT to update idea
        response = await client.put(f"/api/ideas/{idea_id}", json={"content": "Updated content"})
        
        # then: content is updated
        assert response.status_code == 200
        assert response.json()["content"] == "Updated content"

    @pytest.mark.asyncio
    async def test_execute_idea(self, client):
        # given: a draft idea exists
        create_response = await client.post("/api/ideas", json={"content": "Test idea"})
        idea_id = create_response.json()["id"]
        
        # when: POST to execute
        response = await client.post(f"/api/ideas/{idea_id}/execute")
        
        # then: status changes to pending
        assert response.status_code == 200
        result = response.json()
        assert result["old_status"] == "draft"
        assert result["new_status"] == "pending"

    @pytest.mark.asyncio
    async def test_cancel_idea(self, client):
        # given: a pending idea exists
        create_response = await client.post("/api/ideas", json={"content": "Test idea"})
        idea_id = create_response.json()["id"]
        await client.post(f"/api/ideas/{idea_id}/execute")
        
        # when: POST to cancel
        response = await client.post(f"/api/ideas/{idea_id}/cancel")
        
        # then: status changes to cancelled
        assert response.status_code == 200
        result = response.json()
        assert result["new_status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_add_user_message(self, client):
        # given: an idea exists
        create_response = await client.post("/api/ideas", json={"content": "Test idea"})
        idea_id = create_response.json()["id"]
        
        # when: POST to add message
        response = await client.post(
            f"/api/ideas/{idea_id}/messages",
            json={"content": "User instruction"}
        )
        
        # then: message is added
        assert response.status_code == 201
        result = response.json()
        assert result["content"] == "User instruction"
        assert result["type"] == "user_input"


class TestAgentAPI:
    @pytest.mark.asyncio
    async def test_poll_returns_pending_ideas(self, client):
        # given: a pending idea exists
        create_response = await client.post("/api/ideas", json={"content": "Test idea"})
        idea_id = create_response.json()["id"]
        await client.post(f"/api/ideas/{idea_id}/execute")
        
        # when: agent polls
        response = await client.get("/api/agent/poll")
        
        # then: pending ideas are returned
        assert response.status_code == 200
        ideas = response.json()
        assert len(ideas) == 1
        assert ideas[0]["status"] == "pending"

    @pytest.mark.asyncio
    async def test_claim_task(self, client):
        # given: a pending idea exists
        create_response = await client.post("/api/ideas", json={"content": "Test idea"})
        idea_id = create_response.json()["id"]
        await client.post(f"/api/ideas/{idea_id}/execute")
        
        # when: agent claims task
        response = await client.post(
            f"/api/agent/claim/{idea_id}",
            json={"agent_id": "agent-001"}
        )
        
        # then: task is claimed
        assert response.status_code == 200
        result = response.json()
        assert result["new_status"] == "claimed"

    @pytest.mark.asyncio
    async def test_start_execution(self, client):
        # given: a claimed idea exists
        create_response = await client.post("/api/ideas", json={"content": "Test idea"})
        idea_id = create_response.json()["id"]
        await client.post(f"/api/ideas/{idea_id}/execute")
        await client.post(f"/api/agent/claim/{idea_id}", json={"agent_id": "agent-001"})
        
        # when: agent starts execution
        response = await client.post(
            f"/api/agent/start/{idea_id}",
            json={"agent_id": "agent-001"}
        )
        
        # then: status changes to executing
        assert response.status_code == 200
        assert response.json()["new_status"] == "executing"

    @pytest.mark.asyncio
    async def test_submit_feedback(self, client):
        # given: an executing idea exists
        create_response = await client.post("/api/ideas", json={"content": "Test idea"})
        idea_id = create_response.json()["id"]
        await client.post(f"/api/ideas/{idea_id}/execute")
        await client.post(f"/api/agent/claim/{idea_id}", json={"agent_id": "agent-001"})
        await client.post(f"/api/agent/start/{idea_id}", json={"agent_id": "agent-001"})
        
        # when: agent submits feedback
        response = await client.post(
            f"/api/agent/feedback/{idea_id}",
            json={"agent_id": "agent-001", "content": "Progress update"}
        )
        
        # then: feedback is recorded
        assert response.status_code == 200
        
        # verify message was added
        messages_response = await client.get(f"/api/ideas/{idea_id}/messages")
        messages = messages_response.json()
        feedback_messages = [m for m in messages if m["type"] == "agent_feedback"]
        assert len(feedback_messages) >= 1

    @pytest.mark.asyncio
    async def test_ask_user_transitions_to_waiting(self, client):
        # given: an executing idea exists
        create_response = await client.post("/api/ideas", json={"content": "Test idea"})
        idea_id = create_response.json()["id"]
        await client.post(f"/api/ideas/{idea_id}/execute")
        await client.post(f"/api/agent/claim/{idea_id}", json={"agent_id": "agent-001"})
        await client.post(f"/api/agent/start/{idea_id}", json={"agent_id": "agent-001"})
        
        # when: agent asks user
        response = await client.post(
            f"/api/agent/ask/{idea_id}",
            json={"agent_id": "agent-001", "question": "Which option?"}
        )
        
        # then: status changes to waiting_user
        assert response.status_code == 200
        assert response.json()["new_status"] == "waiting_user"

    @pytest.mark.asyncio
    async def test_user_reply_transitions_to_waiting_agent(self, client):
        # given: an idea waiting for user
        create_response = await client.post("/api/ideas", json={"content": "Test idea"})
        idea_id = create_response.json()["id"]
        await client.post(f"/api/ideas/{idea_id}/execute")
        await client.post(f"/api/agent/claim/{idea_id}", json={"agent_id": "agent-001"})
        await client.post(f"/api/agent/start/{idea_id}", json={"agent_id": "agent-001"})
        await client.post(f"/api/agent/ask/{idea_id}", json={"agent_id": "agent-001", "question": "Which option?"})
        
        # when: user replies
        await client.post(f"/api/ideas/{idea_id}/messages", json={"content": "Option A"})
        
        # then: status changes to waiting_agent
        idea_response = await client.get(f"/api/ideas/{idea_id}")
        assert idea_response.json()["status"] == "waiting_agent"

    @pytest.mark.asyncio
    async def test_complete_task(self, client):
        # given: an executing idea exists
        create_response = await client.post("/api/ideas", json={"content": "Test idea"})
        idea_id = create_response.json()["id"]
        await client.post(f"/api/ideas/{idea_id}/execute")
        await client.post(f"/api/agent/claim/{idea_id}", json={"agent_id": "agent-001"})
        await client.post(f"/api/agent/start/{idea_id}", json={"agent_id": "agent-001"})
        
        # when: agent completes task
        response = await client.post(
            f"/api/agent/complete/{idea_id}",
            json={"agent_id": "agent-001", "summary": "Done!"}
        )
        
        # then: status changes to completed
        assert response.status_code == 200
        assert response.json()["new_status"] == "completed"

    @pytest.mark.asyncio
    async def test_fail_task(self, client):
        # given: an executing idea exists
        create_response = await client.post("/api/ideas", json={"content": "Test idea"})
        idea_id = create_response.json()["id"]
        await client.post(f"/api/ideas/{idea_id}/execute")
        await client.post(f"/api/agent/claim/{idea_id}", json={"agent_id": "agent-001"})
        await client.post(f"/api/agent/start/{idea_id}", json={"agent_id": "agent-001"})
        
        # when: agent fails task
        response = await client.post(
            f"/api/agent/fail/{idea_id}",
            json={"agent_id": "agent-001", "reason": "Cannot complete"}
        )
        
        # then: status changes to failed
        assert response.status_code == 200
        assert response.json()["new_status"] == "failed"

    @pytest.mark.asyncio
    async def test_unauthorized_agent_rejected(self, client):
        # given: an executing idea claimed by agent-001
        create_response = await client.post("/api/ideas", json={"content": "Test idea"})
        idea_id = create_response.json()["id"]
        await client.post(f"/api/ideas/{idea_id}/execute")
        await client.post(f"/api/agent/claim/{idea_id}", json={"agent_id": "agent-001"})
        await client.post(f"/api/agent/start/{idea_id}", json={"agent_id": "agent-001"})
        
        # when: different agent tries to complete
        response = await client.post(
            f"/api/agent/complete/{idea_id}",
            json={"agent_id": "agent-002", "summary": "Done!"}
        )
        
        # then: request is rejected
        assert response.status_code == 403


class TestFullWorkflow:
    @pytest.mark.asyncio
    async def test_complete_execution_workflow(self, client):
        # 1. Create idea
        create_response = await client.post("/api/ideas", json={"content": "Build a feature"})
        idea_id = create_response.json()["id"]
        assert create_response.json()["status"] == "draft"
        
        # 2. Execute
        await client.post(f"/api/ideas/{idea_id}/execute")
        
        # 3. Agent polls and claims
        poll_response = await client.get("/api/agent/poll")
        assert len(poll_response.json()) == 1
        
        await client.post(f"/api/agent/claim/{idea_id}", json={"agent_id": "agent-001"})
        
        # 4. Agent starts execution
        await client.post(f"/api/agent/start/{idea_id}", json={"agent_id": "agent-001"})
        
        # 5. Agent provides feedback
        await client.post(f"/api/agent/feedback/{idea_id}", json={"agent_id": "agent-001", "content": "Working on it..."})
        
        # 6. Agent asks user
        await client.post(f"/api/agent/ask/{idea_id}", json={"agent_id": "agent-001", "question": "Need clarification"})
        
        # 7. User replies
        await client.post(f"/api/ideas/{idea_id}/messages", json={"content": "Here is the clarification"})
        
        # 8. Agent continues and completes
        await client.post(f"/api/agent/start/{idea_id}", json={"agent_id": "agent-001"})
        await client.post(f"/api/agent/complete/{idea_id}", json={"agent_id": "agent-001", "summary": "Feature complete"})
        
        # 9. Verify final state
        final_response = await client.get(f"/api/ideas/{idea_id}")
        idea = final_response.json()
        assert idea["status"] == "completed"
        
        # 10. Verify thread has all events
        assert len(idea["messages"]) >= 5  # system events + feedback + question + reply
