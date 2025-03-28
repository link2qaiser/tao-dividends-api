# tests/tasks/test_stake.py (continued)
    # Test function
    result = await _process_sentiment_stake(18, "5FFApaS75bv5pJHfAp2FVLBj9ZaXuFDjEypsaBNc1wCfe52v")
    
    assert result["success"] is True
    assert "message" in result
    assert "Skipped" in result["message"]
    assert result["sentiment_score"] == 0.5

@pytest.mark.asyncio
async def test_process_sentiment_stake_error_handling(mock_sentiment_service, mock_blockchain_service):
    """Test error handling in sentiment stake processing"""
    # Mock sentiment to raise an exception
    mock_sentiment_service.get_subnet_sentiment = AsyncMock(side_effect=Exception("Test error"))
    
    # Test function
    result = await _process_sentiment_stake(18, "5FFApaS75bv5pJHfAp2FVLBj9ZaXuFDjEypsaBNc1wCfe52v")
    
    assert result["success"] is False
    assert "error" in result
    assert "Test error" in result["error"]
    assert result["netuid"] == 18
    assert result["hotkey"] == "5FFApaS75bv5pJHfAp2FVLBj9ZaXuFDjEypsaBNc1wCfe52v"