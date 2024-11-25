from sqlalchemy import Table, Column, Integer, String, Text, Enum, JSON, MetaData

# Metadata object
metadata = MetaData()

# Messages table
messages = Table(
    'messages',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('content', Text, nullable=False),
    Column('chatId', Text, nullable=False),
    Column('messageId', Text, nullable=False),
    Column('role', Enum('assistant', 'user', name='role_type')),
    Column('metadata', JSON),
)

# Chats table
chats = Table(
    'chats',
    metadata,
    Column('id', Text, primary_key=True),
    Column('title', Text, nullable=False),
    Column('createdAt', Text, nullable=False),
    Column('focusMode', Text, nullable=False),
)
