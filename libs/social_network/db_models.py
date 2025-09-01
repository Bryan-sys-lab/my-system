"""
Database Models for Social Network Storage

This module defines SQLAlchemy models for persistent storage of social network data:
- SocialPerson: Stores person information
- SocialRelationship: Stores relationship information
- SocialGraphMetadata: Stores graph metadata and statistics
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, ForeignKey, Index
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class SocialPerson(Base):
    """Database model for storing person information"""

    __tablename__ = 'social_people'

    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    username = Column(String(255))
    platform = Column(String(100), nullable=False)
    profile_url = Column(Text)
    bio = Column(Text)
    location = Column(String(255))
    follower_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    post_count = Column(Integer, default=0)
    verified = Column(Integer, default=0)  # 0=False, 1=True
    metadata_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    outgoing_relationships = relationship(
        "SocialRelationship",
        foreign_keys="SocialRelationship.source_id",
        back_populates="source_person"
    )
    incoming_relationships = relationship(
        "SocialRelationship",
        foreign_keys="SocialRelationship.target_id",
        back_populates="target_person"
    )

    __table_args__ = (
        Index('idx_social_people_platform_username', 'platform', 'username'),
        Index('idx_social_people_created_at', 'created_at'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'platform': self.platform,
            'profile_url': self.profile_url,
            'bio': self.bio,
            'location': self.location,
            'follower_count': self.follower_count,
            'following_count': self.following_count,
            'post_count': self.post_count,
            'verified': bool(self.verified),
            'metadata': self.metadata_json or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SocialPerson':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            name=data['name'],
            username=data.get('username'),
            platform=data['platform'],
            profile_url=data.get('profile_url'),
            bio=data.get('bio'),
            location=data.get('location'),
            follower_count=data.get('follower_count', 0),
            following_count=data.get('following_count', 0),
            post_count=data.get('post_count', 0),
            verified=1 if data.get('verified', False) else 0,
            metadata_json=data.get('metadata', {})
        )


class SocialRelationship(Base):
    """Database model for storing relationship information"""

    __tablename__ = 'social_relationships'

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String(255), ForeignKey('social_people.id'), nullable=False)
    target_id = Column(String(255), ForeignKey('social_people.id'), nullable=False)
    relationship_type = Column(String(100), nullable=False)
    strength = Column(Float, default=0.0)
    platforms = Column(JSON)  # List of platforms where relationship exists
    interaction_count = Column(Integer, default=1)
    first_interaction = Column(DateTime)
    last_interaction = Column(DateTime)
    shared_content = Column(JSON)  # List of shared content IDs
    metadata_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    source_person = relationship("SocialPerson", foreign_keys=[source_id], back_populates="outgoing_relationships")
    target_person = relationship("SocialPerson", foreign_keys=[target_id], back_populates="incoming_relationships")

    __table_args__ = (
        Index('idx_social_relationships_source_target', 'source_id', 'target_id'),
        Index('idx_social_relationships_type', 'relationship_type'),
        Index('idx_social_relationships_strength', 'strength'),
        Index('idx_social_relationships_last_interaction', 'last_interaction'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'source_id': self.source_id,
            'target_id': self.target_id,
            'relationship_type': self.relationship_type,
            'strength': self.strength,
            'platforms': self.platforms or [],
            'interaction_count': self.interaction_count,
            'first_interaction': self.first_interaction.isoformat() if self.first_interaction else None,
            'last_interaction': self.last_interaction.isoformat() if self.last_interaction else None,
            'shared_content': self.shared_content or [],
            'metadata': self.metadata_json or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SocialRelationship':
        """Create from dictionary"""
        return cls(
            source_id=data['source_id'],
            target_id=data['target_id'],
            relationship_type=data['relationship_type'],
            strength=data.get('strength', 0.0),
            platforms=data.get('platforms', []),
            interaction_count=data.get('interaction_count', 1),
            first_interaction=datetime.fromisoformat(data['first_interaction']) if data.get('first_interaction') else None,
            last_interaction=datetime.fromisoformat(data['last_interaction']) if data.get('last_interaction') else None,
            shared_content=data.get('shared_content', []),
            metadata_json=data.get('metadata', {})
        )


class SocialGraphMetadata(Base):
    """Database model for storing graph metadata and statistics"""

    __tablename__ = 'social_graph_metadata'

    id = Column(Integer, primary_key=True, autoincrement=True)
    graph_id = Column(String(255), nullable=False)  # Identifier for the graph (e.g., project_id)
    total_nodes = Column(Integer, default=0)
    total_relationships = Column(Integer, default=0)
    network_density = Column(Float, default=0.0)
    average_path_length = Column(Float, default=0.0)
    network_diameter = Column(Integer, default=0)
    communities_count = Column(Integer, default=0)
    average_clustering_coefficient = Column(Float, default=0.0)

    # Centrality measures (stored as JSON)
    degree_centrality = Column(JSON)
    betweenness_centrality = Column(JSON)
    closeness_centrality = Column(JSON)
    eigenvector_centrality = Column(JSON)
    pagerank_centrality = Column(JSON)

    # Additional statistics
    platform_distribution = Column(JSON)
    relationship_type_distribution = Column(JSON)
    temporal_distribution = Column(JSON)

    # Metadata
    metadata_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_social_graph_metadata_graph_id', 'graph_id'),
        Index('idx_social_graph_metadata_created_at', 'created_at'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'graph_id': self.graph_id,
            'total_nodes': self.total_nodes,
            'total_relationships': self.total_relationships,
            'network_density': self.network_density,
            'average_path_length': self.average_path_length,
            'network_diameter': self.network_diameter,
            'communities_count': self.communities_count,
            'average_clustering_coefficient': self.average_clustering_coefficient,
            'degree_centrality': self.degree_centrality or {},
            'betweenness_centrality': self.betweenness_centrality or {},
            'closeness_centrality': self.closeness_centrality or {},
            'eigenvector_centrality': self.eigenvector_centrality or {},
            'pagerank_centrality': self.pagerank_centrality or {},
            'platform_distribution': self.platform_distribution or {},
            'relationship_type_distribution': self.relationship_type_distribution or {},
            'temporal_distribution': self.temporal_distribution or {},
            'metadata': self.metadata_json or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SocialGraphMetadata':
        """Create from dictionary"""
        return cls(
            graph_id=data['graph_id'],
            total_nodes=data.get('total_nodes', 0),
            total_relationships=data.get('total_relationships', 0),
            network_density=data.get('network_density', 0.0),
            average_path_length=data.get('average_path_length', 0.0),
            network_diameter=data.get('network_diameter', 0),
            communities_count=data.get('communities_count', 0),
            average_clustering_coefficient=data.get('average_clustering_coefficient', 0.0),
            degree_centrality=data.get('degree_centrality', {}),
            betweenness_centrality=data.get('betweenness_centrality', {}),
            closeness_centrality=data.get('closeness_centrality', {}),
            eigenvector_centrality=data.get('eigenvector_centrality', {}),
            pagerank_centrality=data.get('pagerank_centrality', {}),
            platform_distribution=data.get('platform_distribution', {}),
            relationship_type_distribution=data.get('relationship_type_distribution', {}),
            temporal_distribution=data.get('temporal_distribution', {}),
            metadata_json=data.get('metadata', {})
        )


class SocialNetworkStorage:
    """Manager for social network database operations"""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def save_graph(self, graph, graph_id: str):
        """Save a social graph to the database"""
        with self.session_factory() as session:
            try:
                # Save people
                for person in graph.people.values():
                    db_person = SocialPerson.from_dict(person.to_dict())
                    session.merge(db_person)  # Use merge to handle updates

                # Save relationships
                for relationship in graph.relationships.values():
                    db_relationship = SocialRelationship.from_dict(relationship.to_dict())
                    session.merge(db_relationship)

                # Save metadata
                metadata = SocialGraphMetadata.from_dict({
                    'graph_id': graph_id,
                    'total_nodes': len(graph.people),
                    'total_relationships': len(graph.relationships),
                    **graph.get_network_stats()
                })
                session.merge(metadata)

                session.commit()

            except Exception as e:
                session.rollback()
                raise e

    def load_graph(self, graph_id: str):
        """Load a social graph from the database"""
        from .models import SocialGraph, Person, Relationship

        with self.session_factory() as session:
            # Load people
            people_query = session.query(SocialPerson).filter(
                SocialPerson.id.in_(
                    session.query(SocialRelationship.source_id).filter(
                        SocialRelationship.id.in_(
                            session.query(SocialRelationship.id).join(SocialGraphMetadata).filter(
                                SocialGraphMetadata.graph_id == graph_id
                            )
                        )
                    ).union(
                        session.query(SocialRelationship.target_id).filter(
                            SocialRelationship.id.in_(
                                session.query(SocialRelationship.id).join(SocialGraphMetadata).filter(
                                    SocialGraphMetadata.graph_id == graph_id
                                )
                            )
                        )
                    )
                )
            )

            people = {}
            for db_person in people_query:
                person = Person.from_dict(db_person.to_dict())
                people[person.id] = person

            # Load relationships
            relationships_query = session.query(SocialRelationship).join(
                SocialGraphMetadata
            ).filter(SocialGraphMetadata.graph_id == graph_id)

            relationships = {}
            for db_rel in relationships_query:
                relationship = Relationship.from_dict(db_rel.to_dict())
                relationships[f"{relationship.source_id}_{relationship.target_id}_{relationship.relationship_type}"] = relationship

            # Create graph
            graph = SocialGraph()
            for person in people.values():
                graph.add_person(person)
            for relationship in relationships.values():
                graph.add_relationship(relationship)

            return graph

    def get_graph_metadata(self, graph_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a social graph"""
        with self.session_factory() as session:
            metadata = session.query(SocialGraphMetadata).filter_by(graph_id=graph_id).first()
            return metadata.to_dict() if metadata else None

    def update_relationship_strength(self, source_id: str, target_id: str, relationship_type: str, new_strength: float):
        """Update the strength of a relationship"""
        with self.session_factory() as session:
            relationship = session.query(SocialRelationship).filter_by(
                source_id=source_id,
                target_id=target_id,
                relationship_type=relationship_type
            ).first()

            if relationship:
                relationship.strength = new_strength
                relationship.updated_at = datetime.utcnow()
                session.commit()

    def get_relationship_history(self, source_id: str, target_id: str) -> List[Dict[str, Any]]:
        """Get relationship history between two people"""
        with self.session_factory() as session:
            relationships = session.query(SocialRelationship).filter(
                ((SocialRelationship.source_id == source_id) & (SocialRelationship.target_id == target_id)) |
                ((SocialRelationship.source_id == target_id) & (SocialRelationship.target_id == source_id))
            ).order_by(SocialRelationship.created_at).all()

            return [rel.to_dict() for rel in relationships]

    def delete_graph(self, graph_id: str):
        """Delete a social graph from the database"""
        with self.session_factory() as session:
            try:
                # Delete relationships first (due to foreign key constraints)
                session.query(SocialRelationship).filter(
                    SocialRelationship.id.in_(
                        session.query(SocialRelationship.id).join(SocialGraphMetadata).filter(
                            SocialGraphMetadata.graph_id == graph_id
                        )
                    )
                ).delete(synchronize_session=False)

                # Delete people (only if they have no other relationships)
                people_to_delete = session.query(SocialPerson).filter(
                    ~SocialPerson.id.in_(
                        session.query(SocialRelationship.source_id).union(
                            session.query(SocialRelationship.target_id)
                        )
                    )
                )
                people_to_delete.delete(synchronize_session=False)

                # Delete metadata
                session.query(SocialGraphMetadata).filter_by(graph_id=graph_id).delete()

                session.commit()

            except Exception as e:
                session.rollback()
                raise e