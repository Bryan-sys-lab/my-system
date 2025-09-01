"""
Relationship Extractor Module

This module extracts relationships from social media data including:
- Mentions and replies
- Shared content and media
- Follower/following relationships
- Group memberships
- Location-based connections
"""

from typing import List, Dict, Any, Set, Optional
from datetime import datetime
from collections import defaultdict
import re

from .models import Person, Relationship, SocialGraph
from ..storage.models import Item


class RelationshipExtractor:
    """Extracts relationships from social media data"""

    def __init__(self):
        self.mention_pattern = re.compile(r'@(\w+)')
        self.hashtag_pattern = re.compile(r'#(\w+)')
        self.url_pattern = re.compile(r'https?://[^\s]+')

    def extract_from_items(self, items: List[Item]) -> SocialGraph:
        """Extract social relationships from collected items"""
        graph = SocialGraph()

        # Process each item to extract people and relationships
        for item in items:
            self._process_item(item, graph)

        return graph

    def _process_item(self, item: Item, graph: SocialGraph):
        """Process a single item to extract relationships"""
        # Get actual values from SQLAlchemy model
        content = getattr(item, 'content', '') or ''
        meta = getattr(item, 'meta', {}) or {}
        created_at = getattr(item, 'created_at', None)

        if not content and not meta:
            return

        # Extract author information
        author = self._extract_author(item)
        if author:
            graph.add_person(author)

        # Extract relationships based on content

        # Extract mentions
        mentions = self._extract_mentions(content)
        for mention in mentions:
            if mention != author.id if author else True:
                self._add_mention_relationship(graph, author, mention, item, "mention")

        # Extract replies (if this is a reply)
        if self._is_reply(meta):
            reply_to = self._extract_reply_target(meta)
            if reply_to and author:
                self._add_reply_relationship(graph, author, reply_to, item)

        # Extract shared content relationships
        shared_with = self._extract_shared_content_participants(meta)
        for participant in shared_with:
            if author and participant != author.id:
                self._add_shared_content_relationship(graph, author, participant, item)

        # Extract group/collective relationships
        group_members = self._extract_group_members(meta)
        for member in group_members:
            if author and member != author.id:
                self._add_group_relationship(graph, author, member, item)

        # Extract location-based relationships
        location_participants = self._extract_location_participants(meta)
        for participant in location_participants:
            if author and participant != author.id:
                self._add_location_relationship(graph, author, participant, item)

    def _extract_author(self, item: Item) -> Optional[Person]:
        """Extract author information from an item"""
        meta = getattr(item, 'meta', {}) or {}

        # Try different possible author fields based on platform
        author_info = None
        if 'user' in meta:
            author_info = meta['user']
        elif 'author' in meta:
            author_info = meta['author']
        elif 'username' in meta:
            author_info = {'username': meta['username']}
        elif 'handle' in meta:
            author_info = {'username': meta['handle']}

        if not author_info:
            return None

        # Create person ID
        platform = meta.get('platform', 'unknown')
        username = author_info.get('username') or author_info.get('screen_name') or author_info.get('handle')

        if not username:
            return None

        person_id = f"{platform}:{username}"

        # Create person object
        person = Person(
            id=person_id,
            name=str(author_info.get('name', username)),
            username=str(username),
            platform=str(platform),
            profile_url=author_info.get('profile_url') or author_info.get('url'),
            bio=author_info.get('description') or author_info.get('bio'),
            location=author_info.get('location'),
            follower_count=int(author_info.get('followers_count', 0)),
            following_count=int(author_info.get('following_count') or author_info.get('friends_count', 0)),
            verified=bool(author_info.get('verified', False)),
            metadata=dict(author_info) if isinstance(author_info, dict) else {}
        )

        return person

    def _extract_mentions(self, content_or_meta) -> List[str]:
        """Extract mentioned usernames from either raw content string or a meta dict

        Tests sometimes call this with a meta dict (containing 'mentions' or 'entities').
        Be tolerant of None, Mock objects, and nested structures.
        """
        mentions: List[str] = []

        # If it's a mapping/dict-like object, try structured fields first
        if isinstance(content_or_meta, dict):
            meta = content_or_meta
            # direct mentions list
            if meta.get('mentions'):
                for m in meta.get('mentions'):
                    if isinstance(m, dict):
                        uname = m.get('username') or m.get('screen_name') or None
                        if uname:
                            mentions.append(str(uname))
                    elif isinstance(m, str):
                        mentions.append(m)

            # entities.user_mentions
            if meta.get('entities') and isinstance(meta.get('entities'), dict):
                for m in meta['entities'].get('user_mentions', []):
                    if isinstance(m, dict):
                        uname = m.get('username') or m.get('screen_name') or None
                        if uname:
                            mentions.append(str(uname))

            # fall back to scanning text fields if present
            text_fields = ['content', 'text', 'body']
            for field in text_fields:
                if meta.get(field):
                    try:
                        text = str(meta.get(field))
                        for match in self.mention_pattern.finditer(text):
                            mentions.append(match.group(1))
                    except Exception:
                        continue

            return mentions

        # If it's not a dict, try to treat it as a string
        try:
            text = str(content_or_meta or "")
        except Exception:
            return []

        for match in self.mention_pattern.finditer(text):
            username = match.group(1)
            mentions.append(username)

        return mentions

    # Backwards-compatible aliases used in tests
    def _extract_reply_to(self, meta: Dict[str, Any]) -> Optional[str]:
        return self._extract_reply_target(meta)

    def _extract_retweets(self, meta: Dict[str, Any]) -> List[str]:
        """Extract retweeted usernames from meta structures"""
        retweets = []
        if not meta or not isinstance(meta, dict):
            return retweets

        # Look for explicit retweets/retweets list
        if meta.get('retweets'):
            for r in meta.get('retweets'):
                if isinstance(r, dict):
                    uname = r.get('username') or r.get('screen_name')
                    if uname:
                        retweets.append(str(uname))
                elif isinstance(r, str):
                    retweets.append(r)

        # Look for nested retweeted_status.user.screen_name
        if meta.get('retweeted_status') and isinstance(meta.get('retweeted_status'), dict):
            rs = meta['retweeted_status']
            user = rs.get('user')
            if isinstance(user, dict):
                uname = user.get('screen_name') or user.get('username')
                if uname:
                    retweets.append(str(uname))

        return retweets

    def _is_reply(self, meta: Dict[str, Any]) -> bool:
        """Check if the item is a reply"""
        return (
            meta.get('in_reply_to_status_id') is not None or
            meta.get('in_reply_to_user_id') is not None or
            meta.get('reply_to') is not None or
            'reply' in str(meta.get('type', '')).lower()
        )

    def _extract_reply_target(self, meta: Dict[str, Any]) -> Optional[str]:
        """Extract the target of a reply"""
        if meta.get('in_reply_to_screen_name'):
            return meta['in_reply_to_screen_name']
        elif meta.get('reply_to'):
            return meta['reply_to'].get('username') if isinstance(meta['reply_to'], dict) else str(meta['reply_to'])
        return None

    def _extract_shared_content_participants(self, meta: Dict[str, Any]) -> List[str]:
        """Extract participants from shared content"""
        participants = []

        # Check for retweets, shares, etc.
        if meta.get('retweeted_status'):
            rt_user = meta['retweeted_status'].get('user', {}).get('screen_name')
            if rt_user:
                participants.append(rt_user)

        # Check for quoted tweets
        if meta.get('quoted_status'):
            qt_user = meta['quoted_status'].get('user', {}).get('screen_name')
            if qt_user:
                participants.append(qt_user)

        # Check for shared media tags
        if meta.get('entities', {}).get('user_mentions'):
            for mention in meta['entities']['user_mentions']:
                if mention.get('screen_name'):
                    participants.append(mention['screen_name'])

        return participants

    def _extract_group_members(self, meta: Dict[str, Any]) -> List[str]:
        """Extract group members from collective content"""
        members = []

        # Check for group posts or events
        if meta.get('participants'):
            for participant in meta['participants']:
                if isinstance(participant, dict) and participant.get('username'):
                    members.append(participant['username'])
                elif isinstance(participant, str):
                    members.append(participant)

        # Check for event attendees
        if meta.get('attendees'):
            for attendee in meta['attendees']:
                if isinstance(attendee, dict) and attendee.get('username'):
                    members.append(attendee['username'])

        return members

    def _extract_location_participants(self, meta: Dict[str, Any]) -> List[str]:
        """Extract participants from location-based content"""
        participants = []

        # Check for check-ins or location tags
        if meta.get('place') or meta.get('coordinates'):
            # Look for other people at the same location
            # This would typically require additional context from the database
            pass

        return participants

    def _add_mention_relationship(self, graph: SocialGraph, author: Optional[Person],
                                mentioned_username: str, item: Item, rel_type: str = "mention"):
        """Add a mention relationship"""
        if not author:
            return

        meta = getattr(item, 'meta', {}) or {}
        content = getattr(item, 'content', '') or ''
        created_at = getattr(item, 'created_at', None)
        item_id = getattr(item, 'id', None)

        platform = meta.get('platform', 'unknown') if meta else 'unknown'
        target_id = f"{platform}:{mentioned_username}"

        # Create target person if they don't exist
        if target_id not in graph.people:
            target_person = Person(
                id=target_id,
                name=mentioned_username,
                username=mentioned_username,
                platform=platform
            )
            graph.add_person(target_person)

        # Create relationship
        relationship = Relationship(
            source_id=author.id,
            target_id=target_id,
            relationship_type=rel_type,
            strength=0.3,  # Mentions are weaker connections
            platforms={platform},
            interaction_count=1,
            first_interaction=created_at,
            last_interaction=created_at,
            metadata={
                'item_id': str(item_id) if item_id else 'unknown',
            'content_preview': (str(content)[:100]) if content else ''
            }
        )

        graph.add_relationship(relationship)

    def _add_reply_relationship(self, graph: SocialGraph, author: Person,
                              reply_target: str, item: Item):
        """Add a reply relationship"""
        meta = getattr(item, 'meta', {}) or {}
        content = getattr(item, 'content', '') or ''
        created_at = getattr(item, 'created_at', None)
        item_id = getattr(item, 'id', None)

        platform = meta.get('platform', 'unknown') if meta else 'unknown'
        target_id = f"{platform}:{reply_target}"

        # Create target person if they don't exist
        if target_id not in graph.people:
            target_person = Person(
                id=target_id,
                name=reply_target,
                username=reply_target,
                platform=platform
            )
            graph.add_person(target_person)

        # Create relationship
        relationship = Relationship(
            source_id=author.id,
            target_id=target_id,
            relationship_type="reply",
            strength=0.7,  # Replies are stronger connections
            platforms={platform},
            interaction_count=1,
            first_interaction=created_at,
            last_interaction=created_at,
            metadata={
                'item_id': str(item_id) if item_id else 'unknown',
                'content_preview': (str(content)[:100]) if content else ''
            }
        )

        graph.add_relationship(relationship)

    def _add_shared_content_relationship(self, graph: SocialGraph, author: Person,
                                       participant: str, item: Item):
        """Add a shared content relationship"""
        meta = getattr(item, 'meta', {}) or {}
        content = getattr(item, 'content', '') or ''
        created_at = getattr(item, 'created_at', None)
        item_id = getattr(item, 'id', None)

        platform = meta.get('platform', 'unknown') if meta else 'unknown'
        target_id = f"{platform}:{participant}"

        # Create target person if they don't exist
        if target_id not in graph.people:
            target_person = Person(
                id=target_id,
                name=participant,
                username=participant,
                platform=platform
            )
            graph.add_person(target_person)

        # Create relationship
        relationship = Relationship(
            source_id=author.id,
            target_id=target_id,
            relationship_type="shared_content",
            strength=0.8,  # Shared content is a strong connection
            platforms={platform},
            shared_content=[str(item_id) if item_id else 'unknown'],
            interaction_count=1,
            first_interaction=created_at,
            last_interaction=created_at,
            metadata={
                'item_id': str(item_id) if item_id else 'unknown',
                'content_type': meta.get('type', 'post') if meta else 'post',
                'content_preview': (str(content)[:100]) if content else ''
            }
        )

        graph.add_relationship(relationship)

    def _add_group_relationship(self, graph: SocialGraph, author: Person,
                              member: str, item: Item):
        """Add a group relationship"""
        meta = getattr(item, 'meta', {}) or {}
        created_at = getattr(item, 'created_at', None)
        item_id = getattr(item, 'id', None)

        platform = meta.get('platform', 'unknown') if meta else 'unknown'
        target_id = f"{platform}:{member}"

        # Create target person if they don't exist
        if target_id not in graph.people:
            target_person = Person(
                id=target_id,
                name=member,
                username=member,
                platform=platform
            )
            graph.add_person(target_person)

        # Create relationship
        relationship = Relationship(
            source_id=author.id,
            target_id=target_id,
            relationship_type="group_member",
            strength=0.6,  # Group membership is moderately strong
            platforms={platform},
            interaction_count=1,
            first_interaction=created_at,
            last_interaction=created_at,
            metadata={
                'item_id': str(item_id) if item_id else 'unknown',
                'group_context': meta.get('group_name', 'unknown') if meta else 'unknown'
            }
        )

        graph.add_relationship(relationship)

    def _add_location_relationship(self, graph: SocialGraph, author: Person,
                                 participant: str, item: Item):
        """Add a location-based relationship"""
        meta = getattr(item, 'meta', {}) or {}
        created_at = getattr(item, 'created_at', None)
        item_id = getattr(item, 'id', None)

        platform = meta.get('platform', 'unknown') if meta else 'unknown'
        target_id = f"{platform}:{participant}"

        # Create target person if they don't exist
        if target_id not in graph.people:
            target_person = Person(
                id=target_id,
                name=participant,
                username=participant,
                platform=platform
            )
            graph.add_person(target_person)

        # Create relationship
        relationship = Relationship(
            source_id=author.id,
            target_id=target_id,
            relationship_type="location_shared",
            strength=0.4,  # Location sharing is a moderate connection
            platforms={platform},
            interaction_count=1,
            first_interaction=created_at,
            last_interaction=created_at,
            metadata={
                'item_id': str(item_id) if item_id else 'unknown',
                'location': (meta.get('place', {}) or {}).get('full_name', 'unknown') if meta else 'unknown'
            }
        )

        graph.add_relationship(relationship)