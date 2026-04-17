# Helper logic for  small reusable functions (age group, country selection, UUID)

from uuid_extensions import uuid7

def generate_id():
    return str(uuid7())