"""Utilities for encoding and decoding channel and source ID information in message IDs.

This module provides functions to encode channel names and source IDs (like cell IDs)
directly into message IDs, eliminating the need for a separate message cache to track
message metadata.

Format: {channel}:{base_msg_id}#{src_id}

Examples:
    - With channel and src_id: "shell:a1b2c3d4_12345_0#cell-abc123"
    - With channel only: "shell:a1b2c3d4_12345_0"
    - Legacy format (no encoding): "a1b2c3d4_12345_0"
"""

from typing import Optional, Tuple, List
from jupyter_client.session import Session


class MsgIdError(Exception):
    """Base exception for message ID operations."""
    pass


class InvalidMsgIdFormatError(MsgIdError):
    """Raised when a message ID has an invalid format."""
    pass


class InvalidChannelError(MsgIdError):
    """Raised when a channel name contains reserved characters."""
    pass


class InvalidSrcIdError(MsgIdError):
    """Raised when a source ID contains reserved characters."""
    pass


def validate_channel(channel: Optional[str]) -> None:
    """Validate that a channel name doesn't contain reserved characters.

    Args:
        channel: Channel name to validate

    Raises:
        InvalidChannelError: If channel contains ':' character
    """
    if channel is not None and ':' in channel:
        raise InvalidChannelError(
            f"Channel name cannot contain ':' character: {channel}"
        )


def validate_src_id(src_id: Optional[str]) -> None:
    """Validate that a source ID doesn't contain reserved characters.

    Args:
        src_id: Source ID to validate

    Raises:
        InvalidSrcIdError: If src_id contains ':' or '#' characters
    """
    if src_id is not None:
        if ':' in src_id:
            raise InvalidSrcIdError(
                f"Source ID cannot contain ':' character: {src_id}"
            )
        if '#' in src_id:
            raise InvalidSrcIdError(
                f"Source ID cannot contain '#' character: {src_id}"
            )


def create_msg_id(
    base_msg_id: str,
    channel: Optional[str] = None,
    src_id: Optional[str] = None
) -> str:
    """Create a structured message ID with optional channel and source ID encoding.

    Args:
        base_msg_id: Core message ID (e.g., "{session}_{pid}_{counter}")
        channel: Optional channel name (shell, control, etc.)
        src_id: Optional source identifier (e.g., cell ID)

    Returns:
        Formatted message ID string

    Raises:
        InvalidChannelError: If channel contains ':'
        InvalidSrcIdError: If src_id contains ':' or '#'

    Examples:
        >>> create_msg_id("abc123_456_0", "shell", "cell-xyz")
        'shell:abc123_456_0#cell-xyz'
        >>> create_msg_id("abc123_456_1", "control")
        'control:abc123_456_1'
        >>> create_msg_id("abc123_456_2")
        'abc123_456_2'
    """
    validate_channel(channel)
    validate_src_id(src_id)

    if channel is None:
        # Legacy format for backward compatibility
        result = base_msg_id
    else:
        result = f"{channel}:{base_msg_id}"

    if src_id is not None:
        result = f"{result}#{src_id}"

    return result


def parse_msg_id(msg_id: str) -> Tuple[Optional[str], Optional[str], str]:
    """Parse a message ID into its components.

    Args:
        msg_id: Message ID string to parse

    Returns:
        Tuple of (channel, src_id, base_msg_id) where:
        - channel: Channel name ('shell', 'control', etc.) or None for legacy format
        - src_id: Source identifier (e.g., cell ID) or None
        - base_msg_id: Core message ID

    Examples:
        >>> parse_msg_id("shell:abc123_456_0#cell-xyz")
        ('shell', 'cell-xyz', 'abc123_456_0')
        >>> parse_msg_id("control:abc123_456_1")
        ('control', None, 'abc123_456_1')
        >>> parse_msg_id("abc123_456_2")
        (None, None, 'abc123_456_2')
    """
    if not msg_id:
        raise InvalidMsgIdFormatError("Message ID cannot be empty")

    # Split off src_id if present (after #)
    if '#' in msg_id:
        msg_id_part, src_id = msg_id.split('#', 1)
    else:
        msg_id_part = msg_id
        src_id = None

    # Split channel and base msg_id (before :)
    if ':' in msg_id_part:
        channel, base_msg_id = msg_id_part.split(':', 1)
    else:
        # Legacy format - no channel specified
        channel = None
        base_msg_id = msg_id_part

    return channel, src_id, base_msg_id


def extract_channel(msg_id: str) -> Optional[str]:
    """Extract just the channel from a message ID.

    Args:
        msg_id: Message ID string

    Returns:
        Channel name or None if not present

    Examples:
        >>> extract_channel("shell:abc123_456_0#cell-xyz")
        'shell'
        >>> extract_channel("abc123_456_2")
        None
    """
    channel, _, _ = parse_msg_id(msg_id)
    return channel


def extract_src_id(msg_id: str) -> Optional[str]:
    """Extract just the source ID from a message ID.

    Args:
        msg_id: Message ID string

    Returns:
        Source ID or None if not present

    Examples:
        >>> extract_src_id("shell:abc123_456_0#cell-xyz")
        'cell-xyz'
        >>> extract_src_id("shell:abc123_456_1")
        None
    """
    _, src_id, _ = parse_msg_id(msg_id)
    return src_id


def extract_base_msg_id(msg_id: str) -> str:
    """Extract just the base message ID from a message ID.

    Args:
        msg_id: Message ID string

    Returns:
        Base message ID (without channel or src_id encoding)

    Examples:
        >>> extract_base_msg_id("shell:abc123_456_0#cell-xyz")
        'abc123_456_0'
        >>> extract_base_msg_id("abc123_456_2")
        'abc123_456_2'
    """
    _, _, base_msg_id = parse_msg_id(msg_id)
    return base_msg_id


# ============================================================================
# Message-level utilities for websocket connection
# ============================================================================


def encode_channel_in_message_dict(msg_dict: dict, channel: str) -> dict:
    """Encode channel into a message dict's header msg_id.

    This utility is used for client-initiated messages (not from websocket)
    to ensure they have channel encoding for proper state tracking.

    Args:
        msg_dict: Message dictionary with header, parent_header, metadata, content
        channel: Channel name to encode ('shell', 'control', etc.)

    Returns:
        Modified message dict with channel encoded in header msg_id

    Examples:
        >>> msg = session.msg('kernel_info_request')
        >>> msg = encode_channel_in_message_dict(msg, 'shell')
        >>> # msg['header']['msg_id'] now has 'shell:' prefix
    """
    if 'header' in msg_dict and 'msg_id' in msg_dict['header']:
        msg_id = msg_dict['header']['msg_id']
        # Only encode if not already encoded
        if not msg_id.startswith(f"{channel}:"):
            msg_dict['header']['msg_id'] = f"{channel}:{msg_id}"
    return msg_dict


def encode_cell_id_in_message(msg_list: List[bytes], cell_id: str) -> List[bytes]:
    """Encode a cell ID into the header msg_id of a message.

    This utility function encapsulates the session pack/unpack operations needed
    to add a cell ID to a message's header. It's designed to keep the websocket
    connection code lean.

    Args:
        msg_list: Message parts as list of bytes [header, parent_header, metadata, content, ...]
        cell_id: Cell ID to encode into the message

    Returns:
        Modified message list with cell ID encoded in header msg_id

    Examples:
        >>> # msg_list with msg_id "abc123" becomes msg_id "abc123#cell-xyz"
        >>> modified_msg = encode_cell_id_in_message(msg_list, "cell-xyz")
    """
    # Need at least header part
    if not msg_list or len(msg_list) < 1:
        return msg_list

    try:
        session = Session()
        msg_copy = list(msg_list)  # Make a copy to avoid modifying original

        # Unpack header
        header = session.unpack(msg_copy[0])

        # Encode cell ID into msg_id if not already present
        if "msg_id" in header:
            msg_id = header["msg_id"]
            if "#" not in msg_id:  # Only add if not already encoded
                header["msg_id"] = f"{msg_id}#{cell_id}"
                msg_copy[0] = session.pack(header)

        return msg_copy
    except Exception:
        # If encoding fails, return original message
        return msg_list


def strip_encoding_from_message(msg_list: List[bytes]) -> List[bytes]:
    """Strip channel and cell ID encoding from header and parent_header msg_ids.

    This utility function encapsulates the session pack/unpack operations needed
    to strip encoding from a message before sending to the frontend. It's designed
    to keep the websocket connection code lean.

    Args:
        msg_list: Message parts as list of bytes [header, parent_header, metadata, content, ...]

    Returns:
        Modified message list with encoding stripped from msg_ids

    Examples:
        >>> # msg_list with msg_id "shell:abc123#cell-xyz" becomes "abc123"
        >>> clean_msg = strip_encoding_from_message(msg_list)
    """
    # Need at least header and parent_header
    if not msg_list or len(msg_list) < 2:
        return msg_list

    try:
        session = Session()
        msg_copy = list(msg_list)  # Make a copy to avoid modifying original

        # Strip from header msg_id
        header = session.unpack(msg_copy[0])
        if 'msg_id' in header:
            _, _, base_msg_id = parse_msg_id(header['msg_id'])
            header['msg_id'] = base_msg_id
            msg_copy[0] = session.pack(header)

        # Strip from parent_header msg_id
        parent_header = session.unpack(msg_copy[1])
        if 'msg_id' in parent_header and parent_header['msg_id']:
            _, _, base_msg_id = parse_msg_id(parent_header['msg_id'])
            parent_header['msg_id'] = base_msg_id
            msg_copy[1] = session.pack(parent_header)

        return msg_copy
    except Exception:
        # If decoding fails, return original message
        return msg_list

