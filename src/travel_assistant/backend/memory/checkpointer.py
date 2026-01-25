"""Memory checkpointer configuration."""
import os
from contextlib import asynccontextmanager
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

@asynccontextmanager
async def get_async_checkpointer():
    """Get the Async SQLite checkpointer via context manager.
    
    Yields:
        AsyncSqliteSaver: The configured checkpointer.
    """
    # Ensure data directory exists
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    db_path = os.path.join(data_dir, "travel_memory.sqlite")
    conn_string = db_path
    
    async with AsyncSqliteSaver.from_conn_string(conn_string) as saver:
        yield saver
