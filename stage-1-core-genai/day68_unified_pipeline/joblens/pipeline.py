from analyzer import analyze_jd
from store import store_jd
from profile_matcher import match_profile
from gap_analyser import analyze_gap

def run_joblens(candidate_profile: str, job_data: list):

    print("\n" + "=" * 55)
    print("  JOBLENS — AI Job Intelligence Platform")
    print("=" * 55)

# STEP 1 : Analyse and store the JD 
    print(f"\n📥 Processing {len(job_data)} job descriptions...\n")

    for job in job_data:
        structured=analyze_jd(job["jd_text"])
        store_jd(job["jd_text"],job["company"],structured)

        print(f"{job["company"]}-{structured["one_line_summary"]}")

# STEP 2 : Find Matches
    print(f"\n🔍 Finding best matches for your profile...\n")
    matches = match_profile(candidate_profile,top_k=5)

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



    gap = analyze_gap(candidate_profile, best_match["jd_text"], best_match["company"])
    print(f"  Matching skills : {gap['matching_skills']}")
    print(f"  Missing skills  : {gap['missing_skills']}")
    print(f"  Experience gap  : {gap['experience_gap']}")
    print(f"  Gap severity    : {gap['gap_severity']}")
    print(f"  Ready in        : {gap['ready_in_weeks']} weeks")
    print(f"  Top advice      : {gap['top_advice']}")
    print("\n" + "=" * 55)

    return {"matches": matches, "gap_analysis": gap}


    