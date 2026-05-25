from config import embedding_model,collection

def match_profile(profile : str,top_k :int =3,role_type :str =None,remote_ok:bool = False,
                  company :str =None,role :str =None,company_type :str =None,
                  experience_min :int =None,experience_max :int =None,location :str =None) ->list:
    
    profile_embedding = embedding_model.encode(profile)

    conditions=[]
    if role_type:
        conditions.append({"role_type":role_type})
    if experience_min:
        conditions.append({"experience_min":{"$gte":experience_min}})
    if remote_ok:
        conditions.append({"remote_ok":True})
    if company:
        conditions.append({"company":company})
    if company_type:
        conditions.append({"company_type":company_type})
    if experience_max:
        conditions.append({"experience_max":{"$lte":experience_max}})
    if location:
        conditions.append({"location":location})
    
    where_filter=None
    if len(conditions)==1:
        where_filter=conditions[0]
    if len(conditions)>1:
        where_filter={"$and":conditions}


    result = collection.query(
        query_embeddings=profile_embedding,
        n_results=top_k,
        where=where_filter
    )

    MINIMUM_SIMILARITY = 0.35

    matches=[]

    for doc,distance,meta in zip(result["documents"][0],result["distances"][0],result["metadatas"][0]):
        similarity = 1-distance
        if similarity >= MINIMUM_SIMILARITY:
            matches.append({
                "company": meta["company"],
                "role": meta["role"],
                "score": round(similarity, 3),
                "location": meta["location"],
                "remote_ok": meta["remote_ok"],
                "experience": f"{meta['experience_min']}-{meta['experience_max']}yrs",
                "jd_text": doc
            })


    if not matches:
        print("No confident matches found. Showing best available:")
        for doc, distance, meta in zip(result["documents"][0],result["distances"][0],result["metadatas"][0]):
            similarity = 1 - distance
            matches.append({
                "company": meta["company"],
                "role": meta["role"],
                "score": round(similarity, 3),
                "location": meta.get("location", "not specified"),
                "remote_ok": meta.get("remote_ok", False),
                "experience": f"{meta['experience_min']}-{meta['experience_max']}yrs",
                "jd_text": doc,
                "low_confidence": True 
            })
    return sorted(matches,key =lambda x:x["score"],reverse=True)