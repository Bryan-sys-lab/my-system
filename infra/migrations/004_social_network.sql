-- Migration: 004_social_network.sql
-- Description: Create tables for social network analysis
-- Created: 2025-01-01

-- Create social_people table
CREATE TABLE IF NOT EXISTS social_people (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    username VARCHAR(255),
    platform VARCHAR(100) NOT NULL,
    profile_url TEXT,
    bio TEXT,
    location VARCHAR(255),
    follower_count INTEGER DEFAULT 0,
    following_count INTEGER DEFAULT 0,
    post_count INTEGER DEFAULT 0,
    verified INTEGER DEFAULT 0, -- 0=False, 1=True
    metadata_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create social_relationships table
CREATE TABLE IF NOT EXISTS social_relationships (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    source_id VARCHAR(255) NOT NULL,
    target_id VARCHAR(255) NOT NULL,
    relationship_type VARCHAR(100) NOT NULL,
    strength FLOAT DEFAULT 0.0,
    platforms JSON, -- List of platforms where relationship exists
    interaction_count INTEGER DEFAULT 1,
    first_interaction TIMESTAMP NULL,
    last_interaction TIMESTAMP NULL,
    shared_content JSON, -- List of shared content IDs
    metadata_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES social_people(id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES social_people(id) ON DELETE CASCADE
);

-- Create social_graph_metadata table
CREATE TABLE IF NOT EXISTS social_graph_metadata (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    graph_id VARCHAR(255) NOT NULL,
    total_nodes INTEGER DEFAULT 0,
    total_relationships INTEGER DEFAULT 0,
    network_density FLOAT DEFAULT 0.0,
    average_path_length FLOAT DEFAULT 0.0,
    network_diameter INTEGER DEFAULT 0,
    communities_count INTEGER DEFAULT 0,
    average_clustering_coefficient FLOAT DEFAULT 0.0,
    degree_centrality JSON,
    betweenness_centrality JSON,
    closeness_centrality JSON,
    eigenvector_centrality JSON,
    pagerank_centrality JSON,
    platform_distribution JSON,
    relationship_type_distribution JSON,
    temporal_distribution JSON,
    metadata_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_social_people_platform_username ON social_people(platform, username);
CREATE INDEX IF NOT EXISTS idx_social_people_created_at ON social_people(created_at);

CREATE INDEX IF NOT EXISTS idx_social_relationships_source_target ON social_relationships(source_id, target_id);
CREATE INDEX IF NOT EXISTS idx_social_relationships_type ON social_relationships(relationship_type);
CREATE INDEX IF NOT EXISTS idx_social_relationships_strength ON social_relationships(strength);
CREATE INDEX IF NOT EXISTS idx_social_relationships_last_interaction ON social_relationships(last_interaction);

CREATE INDEX IF NOT EXISTS idx_social_graph_metadata_graph_id ON social_graph_metadata(graph_id);
CREATE INDEX IF NOT EXISTS idx_social_graph_metadata_created_at ON social_graph_metadata(created_at);

-- Create a view for relationship summary
CREATE OR REPLACE VIEW social_relationship_summary AS
SELECT
    relationship_type,
    COUNT(*) as total_relationships,
    AVG(strength) as avg_strength,
    MAX(strength) as max_strength,
    MIN(strength) as min_strength,
    SUM(interaction_count) as total_interactions
FROM social_relationships
GROUP BY relationship_type;

-- Create a view for platform statistics
CREATE OR REPLACE VIEW social_platform_stats AS
SELECT
    platform,
    COUNT(*) as total_people,
    SUM(follower_count) as total_followers,
    SUM(following_count) as total_following,
    AVG(follower_count) as avg_followers,
    AVG(following_count) as avg_following
FROM social_people
GROUP BY platform;

-- Create a view for network overview
CREATE OR REPLACE VIEW social_network_overview AS
SELECT
    gm.graph_id,
    gm.total_nodes,
    gm.total_relationships,
    gm.network_density,
    gm.average_path_length,
    gm.network_diameter,
    gm.communities_count,
    gm.average_clustering_coefficient,
    gm.created_at as last_updated
FROM social_graph_metadata gm
ORDER BY gm.created_at DESC;

-- Insert sample data (optional - for testing)
-- This would be populated by the application

COMMIT;