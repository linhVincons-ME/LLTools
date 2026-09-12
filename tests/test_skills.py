import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from app.database import (
    init_db,
    get_dictation_list,
    get_shadowing_list,
    get_reading_articles_list,
    get_reading_article_by_id,
    get_writing_prompts_list,
    add_custom_vocab,
    get_vocab_items,
)
from app.services.skills_service import SkillsService


def test_skills_system():
    print("Initializing database with 4 skills tables...")
    init_db()

    # 1. Test Listening (Dictation)
    dictations = get_dictation_list()
    assert len(dictations) > 0, f"Expected dictation exercises, got {len(dictations)}"
    print(f"✓ Dictations seeded: {len(dictations)} exercises")

    first_d = dictations[0]
    # Test diff with minor typo
    eval_res = SkillsService.evaluate_dictation(first_d, first_d["transcript"])
    assert eval_res.accuracy_score == 100.0
    assert eval_res.is_perfect is True
    assert eval_res.xp_earned == 25
    print(f"✓ Dictation perfect evaluation passed: {eval_res.accuracy_score}%")

    # Test diff with missing/wrong words
    partial_text = "I start my morning with coffee"
    partial_res = SkillsService.evaluate_dictation(first_d, partial_text)
    assert 0 < partial_res.accuracy_score < 100.0
    print(f"✓ Dictation partial evaluation passed: {partial_res.accuracy_score}%")

    # 2. Test Speaking (Shadowing)
    shadowings = get_shadowing_list()
    assert len(shadowings) > 0, f"Expected shadowing exercises, got {len(shadowings)}"
    print(f"✓ Shadowing seeded: {len(shadowings)} exercises")

    first_s = shadowings[0]
    shw_res = SkillsService.evaluate_shadowing(first_s, first_s["text"])
    assert shw_res.similarity_score == 100.0
    assert shw_res.accuracy_level == "Xuất sắc"
    print(f"✓ Shadowing evaluation passed: similarity={shw_res.similarity_score}% ({shw_res.accuracy_level})")

    # 3. Test Reading (Smart Reading Room & 1-Click Lexicon)
    articles = get_reading_articles_list()
    assert len(articles) > 0, f"Expected reading articles, got {len(articles)}"
    print(f"✓ Reading articles seeded: {len(articles)} articles")

    full_art = get_reading_article_by_id(articles[0]["id"])
    assert len(full_art["paragraphs_en"]) > 0
    assert len(full_art["vocabulary_glossary"]) > 0
    print(f"✓ Reading article detail passed: {full_art['title_en']} ({len(full_art['paragraphs_en'])} paras)")

    # Test 1-click add custom vocab
    add_custom_vocab(
        word="Decoupled",
        ipa="/diːˈkʌp.əld/",
        meaning_vi="Tách rời, không còn ràng buộc",
        category="Reading Room",
        level="B2"
    )
    vocab_items = get_vocab_items(search="Decoupled")
    assert len(vocab_items) > 0
    print(f"✓ 1-Click Lexicon save to flashcards passed: '{vocab_items[0]['word']}' added")

    # 4. Test Writing (Writing Lab)
    prompts = get_writing_prompts_list()
    assert len(prompts) > 0, f"Expected writing prompts, got {len(prompts)}"
    print(f"✓ Writing prompts seeded: {len(prompts)} prompts")

    sample_essay = (
        "Consistency is very important when mastering English. Furthermore, small daily habits "
        "allow busy professionals to accomplish remarkable transformations over time. "
        "Consequently, self-paced interactive software facilitates long term fluency."
    )
    write_res = SkillsService.evaluate_writing(sample_essay, prompts[0]["id"])
    assert write_res.word_count > 25
    assert write_res.lexical_richness_score > 30
    assert len(write_res.advanced_words_found) > 0
    print(f"✓ Writing evaluation passed: {write_res.word_count} words, rating={write_res.overall_rating}, richness={write_res.lexical_richness_score}/100")
    print(f"   Advanced words: {write_res.advanced_words_found}")

    print("\n🎉 ALL 4 CORE SKILLS VERIFIED SUCCESSFULLY!")


if __name__ == "__main__":
    test_skills_system()
