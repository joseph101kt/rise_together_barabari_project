CREATE OR REPLACE VIEW module_card_view AS
SELECT
    m.id,
    m.parent_id,
    m.module_type,
    m.title,
    m.description,
    m.estimated_completion_time,
    m.created_by,
    m.order_index,
    m.created_at,
    m.updated_at,
    COUNT(DISTINCT ml.link_id)     AS resource_count,
    COUNT(DISTINCT ms.skill_id)    AS skill_count,
    COUNT(DISTINCT mstar.user_id)  AS star_count
FROM modules m
LEFT JOIN module_links  ml    ON ml.module_id    = m.id
LEFT JOIN module_skills ms    ON ms.module_id    = m.id
LEFT JOIN module_stars  mstar ON mstar.module_id = m.id
GROUP BY m.id;