#!/usr/bin/env python3
"""Test improved streaming display with long content."""

import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_overflow():
    """Test streaming display with long content."""
    from src.agents.base_agent import StreamingCallbackHandler
    from rich.console import Console
    
    console = Console()
    handler = StreamingCallbackHandler("TestAgent", console, verbose=True)
    
    # Simulate long content
    handler.on_llm_start({}, [])
    
    # Generate very long content
    long_text = "This is a very long line that should wrap properly and demonstrate the improved streaming display. " * 50
    long_text += "\n" + "Another long line with different content to show line wrapping. " * 30
    long_text += "\n" + "Third line with even more content to test overflow handling. " * 40
    
    # Stream it token by token
    for char in long_text:
        handler.on_llm_new_token(char)
        await asyncio.sleep(0.01)
    
    handler.on_llm_end(long_text)
    print("✅ Overflow test completed!")

if __name__ == "__main__":
    asyncio.run(test_overflow())
