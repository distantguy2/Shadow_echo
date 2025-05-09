# src/core/skills.py

from .entities import SkillCard, SkillType

# Thư viện kỹ năng có thể chọn trong phase SKILL_SELECT
SKILL_LIBRARY = {
    "blood_lust": SkillCard(
        skill_id="blood_lust",
        name="Blood Lust",
        description="Increase damage after each kill and heal on kill.",
        icon="🩸",
        type=SkillType.PASSIVE,
        effect={"damage_bonus": 5, "stackable": True, "heal_per_kill": [10, 15, 20, 25, 30]}
    ),
    "heal_wave": SkillCard(
        skill_id="heal_wave",
        name="Heal Wave",
        description="Restore health to yourself and nearby allies.",
        icon="💧",
        type=SkillType.SUPPORT,
        cooldown=20.0,
        effect={"heal": 40, "radius": 100}
    ),
    "fireball": SkillCard(
        skill_id="fireball",
        name="Fireball",
        description="Cast a fireball that explodes on impact.",
        icon="🔥",
        type=SkillType.ACTIVE,
        cooldown=8.0,
        effect={"damage": 50, "aoe_radius": 50}
    ),
    "shadowstep": SkillCard(
        skill_id="shadowstep",
        name="Shadowstep",
        description="Teleport a short distance instantly.",
        icon="🌑",
        type=SkillType.ACTIVE,
        cooldown=12.0,
        effect={"range": 150}
    ),
    "divine_shield": SkillCard(
        skill_id="divine_shield",
        name="Divine Shield",
        description="Negate the next source of damage.",
        icon="🛡️",
        type=SkillType.SUPPORT,
        cooldown=30.0,
        effect={"duration": 5, "negate_damage": True}
    ),
    "focus_mind": SkillCard(
        skill_id="focus_mind",
        name="Focus Mind",
        description="Reduce cooldowns temporarily.",
        icon="🧠",
        type=SkillType.PASSIVE,
        effect={"cooldown_reduction": 0.2}
    ),
}
