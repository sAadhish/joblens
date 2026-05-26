from analyzer import analyze_jd
from store import store_jd
from profile_matcher import match_profile
from gap_analyser import analyze_gap
from logger import logger


def run_joblens(candidate_profile: str, job_data: list):

    if not candidate_profile or not candidate_profile.strip():
        logger.error("Empty candidate profile provided")
        return None
    
    if not job_data :
        logger.error("Empty candidate profile provided")
        return None
    
    logger.info(f"Pipeline started — {len(job_data)} JDs, profile length: {len(candidate_profile)} chars")

    print("\n" + "=" * 55)
    print("  JOBLENS — AI Job Intelligence Platform")
    print("=" * 55)


# STEP 1 : Analyse and store the JD 
    print(f"\n📥 Processing {len(job_data)} job descriptions...\n")
    
    stored_count = 0

    for job in job_data:
        structured=analyze_jd(job["jd_text"])

        if not structured:
            # This JD failed — log it, skip it, continue with others
            logger.warning(f"Skipping {job["company"]} — analysis failed")
            print(f"{job["company"]} — skipped (analysis failed)")
            continue


        doc_id = store_jd(job["jd_text"],job["company"],structured)

        if not doc_id:
            logger.warning(f"Skipping {job["company"]} — storage failed")
            print(f"{job["company"]} — skipped (storage failed)")
            continue
        print(f"{job["company"]}-{structured["one_line_summary"]}")

        stored_count += 1
        print(f"{job["company"]} — {structured['one_line_summary']}")

    logger.info(f"Processing complete — {stored_count}/{len(job_data)} JDs stored")
    
    if stored_count == 0:
        logger.error("No JDs stored — cannot match profile")
        print("\nNo JDs processed successfully.")
        return None


# STEP 2 : Find Matches
    print(f"\n🔍 Finding best matches for your profile...\n")

    try:
        matches = match_profile(candidate_profile,top_k=5)
    except Exception as e:
        logger.error(f"Profile matching failed: {e}")
        return None

    if not matches:
        print("No confident matches found")
        return 
    
    for i, match in enumerate(matches):
        confidence = "low confidence" if match.get("low_confidence") else ""
        print(f"  Rank {i+1}: {match['company']} — {match['role']}")
        print(f"           Score: {match['score']} | "
              f"{match['location']} | "
              f"Remote: {match['remote_ok']} | "
              f"{match['experience']}")
        
        
    # STEP 3 — Gap analysis on best match
    best_match= matches[0]


    try :
        gap = analyze_gap(candidate_profile, best_match["jd_text"], best_match["company"])
        print(f"  Matching skills : {gap['matching_skills']}")
        print(f"  Missing skills  : {gap['missing_skills']}")
        print(f"  Experience gap  : {gap['experience_gap']}")
        print(f"  Gap severity    : {gap['gap_severity']}")
        print(f"  Ready in        : {gap['ready_in_weeks']} weeks")
        print(f"  Top advice      : {gap['top_advice']}")
        print("\n" + "=" * 55)
    
    except Exception as e :
        logger.error(f"Gap analysis failed: {e}")
        print("  Gap analysis unavailable")
    
    print("\n" + "=" * 55)
    logger.info("Pipeline completed successfully")

    return {"matches": matches, "gap_analysis": gap}


    