-- Database Update Script for Module Enhancement Feature
-- Run this on your production database if it doesn't have the new columns

-- Add new columns to pages table
ALTER TABLE pages ADD COLUMN IF NOT EXISTS module_description TEXT;
ALTER TABLE pages ADD COLUMN IF NOT EXISTS module_color_primary VARCHAR(20);
ALTER TABLE pages ADD COLUMN IF NOT EXISTS module_color_secondary VARCHAR(20);

-- Update RIASEC module (Page 1)
UPDATE pages SET 
  module_emoji = '🎯',
  chapter_number = 1,
  estimated_minutes = 5,
  module_description = 'Discover your career personality type based on Holland Codes. Find out what truly energizes you and which work environments match your natural preferences.',
  module_color_primary = '#8b5cf6',
  module_color_secondary = '#3b82f6'
WHERE id = 1;

-- Update Big Five module (Page 2)
UPDATE pages SET 
  module_emoji = '🧠',
  chapter_number = 2,
  estimated_minutes = 5,
  module_description = 'Explore the Big Five personality traits that shape how you think, feel, and interact with the world. Understand your unique psychological profile.',
  module_color_primary = '#14b8a6',
  module_color_secondary = '#10b981'
WHERE id = 2;

-- Update Behavioral module (Page 3)
UPDATE pages SET 
  module_emoji = '⚡',
  chapter_number = 3,
  estimated_minutes = 4,
  module_description = 'Uncover how you respond to pressure, challenges, and stressful situations. Learn about your behavioral tendencies and work style preferences.',
  module_color_primary = '#f59e0b',
  module_color_secondary = '#ec4899'
WHERE id = 3;

-- Verify the updates
SELECT id, title, module_name, module_emoji, chapter_number, module_color_primary, module_color_secondary 
FROM pages 
ORDER BY order_index;
