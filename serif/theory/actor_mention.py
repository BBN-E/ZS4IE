from serif.theory.actor_mention_theory import ActorMentionTheory
from serif.theory.mention import Mention
from serif.xmlio import _ReferenceAttribute, _SimpleAttribute, _TextOfElement


class ActorMention(ActorMentionTheory):
    mention = _ReferenceAttribute('mention_id', cls=Mention, is_required=True)
    sentence_theory = _ReferenceAttribute('sentence_theory_id', cls="SentenceTheory")
    source_note = _SimpleAttribute(is_required=True, default="")
    # For Proper Name Actor Mentions:
    actor_db_name = _SimpleAttribute()
    actor_uid = _SimpleAttribute(int)
    actor_code = _SimpleAttribute()
    actor_pattern_uid = _SimpleAttribute(int)
    is_acronym = _SimpleAttribute(bool)
    requires_context = _SimpleAttribute(bool)
    actor_name = _SimpleAttribute()
    pattern_confidence_score = _SimpleAttribute(float)
    importance_score = _SimpleAttribute(float)

    # For Composite Actor Mentions:
    paired_actor_uid = _SimpleAttribute(int)
    paired_actor_code = _SimpleAttribute()
    paired_actor_pattern_uid = _SimpleAttribute(int)
    paired_actor_name = _SimpleAttribute()
    paired_agent_uid = _SimpleAttribute(int)
    paired_agent_code = _SimpleAttribute()
    paired_agent_pattern_uid = _SimpleAttribute(int)
    paired_agent_name = _SimpleAttribute()
    actor_agent_pattern = _SimpleAttribute()

    # For locations resolved to the icews DB
    geo_country = _SimpleAttribute()
    geo_latitude = _SimpleAttribute()
    geo_longitude = _SimpleAttribute()
    geo_uid = _SimpleAttribute()
    geo_text = _SimpleAttribute()

    # Country info
    country_id = _SimpleAttribute(int)
    iso_code = _SimpleAttribute()
    country_info_actor_id = _SimpleAttribute(int)
    country_info_actor_code = _SimpleAttribute()

    # Scores - don't necessarily exist
    pattern_match_score = _SimpleAttribute(float)
    association_score = _SimpleAttribute(float)
    edit_distance_score = _SimpleAttribute(float)
    georesolution_score = _SimpleAttribute(float)
    confidence = _SimpleAttribute(float)

    # Note: this attribute will be empty unless the
    # "icews_include_actor_names_in_serifxml" parameter is enabled.
    name = _TextOfElement(strip=True)
