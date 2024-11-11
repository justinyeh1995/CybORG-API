"""
We are onto upgrading the game endpoints from no api auth to using jwt authentication
"""

import pytest
from fastapi.testclient import TestClient

from api.v1.FastAPI import models
from api.v1.FastAPI.crud import crud_game as crud


def test_create_game(client: TestClient, test_user_jwt_token):
    """
    Check an id is returned
    """
    assert test_user_jwt_token is not None
    
    r = client.post(
        "/api/games/start",
        headers=test_user_jwt_token,
        json={
            "red_agent": "B_lineAgent", 
            "steps": 10, 
            "blue_agent": "BlueReactRemoveAgent", 
            "wrapper": "simple"
        }
    )
    
    response = r.json()

    assert r.status_code == 200
    assert response.get("game_id") is not None

def test_next_step():
    """
    Check given an id, it can run the next step and return a snapshot
    """
    pass

def test_delete_game():
    """
    Check given an id, it can delete the game and return the count of deleted game states
    """
    pass
    