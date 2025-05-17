from fastapi import Depends, HTTPException, APIRouter, Body, Path,Query
from pydantic import BaseModel
from typing import Optional
from model.member_model import Member, MemberUpdate
from utils.db import members_collection

router = APIRouter()


class PhoneLookup(BaseModel):
    phone: str


MEMBER_ID_COUNTER = 2000

@router.post("/register_member", response_model=dict)
async def register_member(member: Member):
    # Check for duplicate ID or email
    if members_collection.find_one({"$or": [{"id": member.id}, {"email": member.email}]}):
        raise HTTPException(status_code=400, detail="Member with this ID or email already exists.")
    
    # Generate a new ID and make sure it's a string
    # global MEMBER_ID_COUNTER
    # member.id = str(MEMBER_ID_COUNTER)
    # MEMBER_ID_COUNTER += 1

    # Insert into collection
    result = members_collection.insert_one(member.model_dump())
    return {"message": "Member registered successfully", "member_id": str(result.inserted_id)}

@router.post("/register_new_user_request", response_model=dict)
async def register_member(member: Member):
    # Check for duplicate ID or email
    if members_collection.find_one({"$or": [{"id": member.id}, {"email": member.email}]}):
        raise HTTPException(status_code=400, detail="Member with this ID or email already exists.")
    
    # Generate a new ID and make sure it's a string
    global MEMBER_ID_COUNTER
    member.id = str(MEMBER_ID_COUNTER)
    MEMBER_ID_COUNTER += 1

    # Insert into collection
    result = members_collection.insert_one(member.model_dump())
    return {"message": "Member registered successfully", "member_id": str(result.inserted_id)}

@router.post("/member/phone", response_model=dict)
async def get_member_by_phone_body(payload: PhoneLookup = Body(...)):
    phone = payload.phone
    member = members_collection.find_one({
        "phone": phone,
        "member_true": True  # Ensure this condition is met
    })
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found with this phone number and member_true = true.")
    
    member["_id"] = str(member["_id"])
    return member

@router.put("/member/update/{id}", response_model=dict)
async def update_member(id: str = Path(...), update_payload: MemberUpdate = Body(...)):
    updates = {k: v for k, v in update_payload.model_dump().items() if v is not None}

    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update.")

    result = members_collection.update_one({"id": id}, {"$set": updates})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"Member with id '{id}' not found.")

    return {"message": "Member updated successfully", "updated_fields": list(updates.keys())}

@router.get("/all/members", response_model=dict)
async def get_all_members():
    members = []
    for member in members_collection.find():
        member["_id"] = str(member["_id"])  # Convert ObjectId to string
        members.append(member)
    
    return {"members": members}

@router.get("/members/filter", response_model=dict)
async def filter_members(
    member_true: Optional[bool] = Query(None),
    amount_subscription: Optional[bool] = Query(None)
):
    query = {}

    if member_true is not None:
        query["member_true"] = member_true

    if amount_subscription is not None:
        query["amount_subscription"] = amount_subscription

    filtered_members = []
    for member in members_collection.find(query):
        member["_id"] = str(member["_id"])
        filtered_members.append(member)

    return {"filtered_members": filtered_members}

@router.get("/non_members", response_model=dict)
async def get_non_members():
    members = []
    for member in members_collection.find({"member_true": False}):
        member["_id"] = str(member["_id"])  # Convert ObjectId to string
        members.append(member)
    
    return {"members": members}


from fastapi import Request

@router.get("/members/search", response_model=dict)
#GET /members/search?phone=1234567890
async def search_members(request: Request):
    # Extract query params from URL
    query_params = dict(request.query_params)

    if not query_params:
        raise HTTPException(status_code=400, detail="No search parameters provided.")

    query = {}

    for key, value in query_params.items():
        # Convert booleans and numbers from string if needed
        if value.lower() == "true":
            query[key] = True
        elif value.lower() == "false":
            query[key] = False
        elif value.isdigit():
            query[key] = int(value)
        else:
            query[key] = value

    matched_members = []
    for member in members_collection.find(query):
        member["_id"] = str(member["_id"])
        matched_members.append(member)

    return {"matched_members": matched_members}

@router.delete("/member/delete/{id}", response_model=dict)
async def delete_member(id: str = Path(...)):
    result = members_collection.delete_one({"id": id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Member with id '{id}' not found.")
    
    return {"message": f"Member with id '{id}' deleted successfully."}


@router.get("/member/{id}", response_model=dict)
async def get_member_by_id(id: str = Path(...)):
    member = members_collection.find_one({"id": id})
    
    if not member:
        raise HTTPException(status_code=404, detail=f"Member with id '{id}' not found.")
    
    # Convert ObjectId to string for JSON serialization
    if "_id" in member:
        member["_id"] = str(member["_id"])
    
    return member
@router.get("/members/total-paid", response_model=dict)
async def get_total_amount_paid():
    members = list(members_collection.find())

    total_paid = 0
    for member in members:
        total_paid += float(member.get("amount_paid", 0))  # Adjust key if needed

    return {"total_members": len(members), "total_amount_paid": total_paid}
@router.get("/members/no-subscription", response_model=list)
async def get_members_no_subscription():
    members = list(members_collection.find({"amount_paid_subscription": 0}))
    for member in members:
        member["_id"] = str(member["_id"])
    return members


@router.get("/members/no-membership", response_model=list)
async def get_members_no_membership():
    members = list(members_collection.find({"amount_paid_registration": 0}))
    for member in members:
        member["_id"] = str(member["_id"])
    return members
@router.get("/members/payment-totals", response_model=dict)
async def get_payment_totals():
    members = list(members_collection.find({}))
    
    total_registration = 0
    total_subscription = 0

    for member in members:
        total_registration += member.get("amount_paid_registration", 0)
        total_subscription += member.get("amount_paid_subscription", 0)

    return {
        "total_registration": total_registration,
        "total_subscription": total_subscription
    }
