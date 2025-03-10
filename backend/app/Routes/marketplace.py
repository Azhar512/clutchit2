# api/marketplace.py - Marketplace API endpoints

from flask import Blueprint, request, jsonify, g
from flask_cors import cross_origin
from functools import wraps
import stripe
import uuid
from datetime import datetime, timedelta

from backend.app.models.marketplace import PickListing, Transaction
from backend.app.models.user import User, Subscription
from backend.app.services.stripe_service import process_marketplace_payment
from backend.app.utils.auth_middleware import auth_required, admin_required
from backend.app.utils.validators import validate_listing_data
from backend.config import STRIPE_SECRET_KEY, PLATFORM_FEE_PERCENT


marketplace_bp = Blueprint('marketplace', __name__, url_prefix='/api/marketplace')

# Initialize Stripe
stripe.api_key = STRIPE_SECRET_KEY

# Subscription tier constants
BASIC_TIER = "basic"
PREMIUM_TIER = "premium"
UNLIMITED_TIER = "unlimited"

def premium_required(f):
    """Decorator to check if user has premium or unlimited subscription"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = g.user_id
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        subscription = Subscription.get_by_user_id(user_id)
        if not subscription or subscription.tier == BASIC_TIER:
            return jsonify({
                "error": "Premium or Unlimited subscription required",
                "subscription_required": True
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

@marketplace_bp.route('/listings', methods=['GET'])
@auth_required
def get_listings():
    """Get all available marketplace listings with pagination"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    sport = request.args.get('sport')
    bet_type = request.args.get('bet_type')
    sort_by = request.args.get('sort_by', 'created_at')  # created_at, price, popularity
    sort_dir = request.args.get('sort_dir', 'desc')
    
    # Build query filters
    filters = {'active': True}
    if sport:
        filters['sport'] = sport
    if bet_type:
        filters['bet_type'] = bet_type
    
    # Get user subscription to determine access
    user_id = g.user_id
    subscription = Subscription.get_by_user_id(user_id)
    
    # Get paginated listings
    listings, total = PickListing.get_listings(
        page=page, 
        per_page=per_page, 
        filters=filters,
        sort_by=sort_by,
        sort_dir=sort_dir
    )
    
    # Filter listings based on subscription tier
    # Basic users can see but not sell picks
    # Premium/Unlimited users can both buy and sell
    
    # Prepare response
    response = {
        "listings": [listing.to_dict() for listing in listings],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page
        },
        "user_can_sell": subscription and subscription.tier in [PREMIUM_TIER, UNLIMITED_TIER]
    }
    
    return jsonify(response)

@marketplace_bp.route('/listings/<listing_id>', methods=['GET'])
@auth_required
def get_listing_detail(listing_id):
    """Get detailed information about a specific listing"""
    listing = PickListing.get_by_id(listing_id)
    
    if not listing:
        return jsonify({"error": "Listing not found"}), 404
    
    # Check if user owns this listing
    user_id = g.user_id
    is_owner = listing.seller_id == user_id
    
    # Check if user has purchased this listing
    has_purchased = Transaction.has_user_purchased(user_id, listing_id)
    
    # Get seller info
    seller = User.get_by_id(listing.seller_id)
    
    response = {
        "listing": listing.to_dict(),
        "is_owner": is_owner,
        "has_purchased": has_purchased,
        "seller": {
            "username": seller.username,
            "performance": {
                "win_rate": seller.get_win_rate(),
                "total_picks_sold": seller.get_total_picks_sold()
            }
        }
    }
    
    # If user owns or has purchased, include full pick details
    if is_owner or has_purchased:
        response["listing"]["full_details"] = listing.get_full_details()
    
    return jsonify(response)

@marketplace_bp.route('/listings', methods=['POST'])
@auth_required
@premium_required
def create_listing():
    """Create a new marketplace listing (Premium/Unlimited only)"""
    user_id = g.user_id
    data = request.json
    
    # Validate input data
    validation_result = validate_listing_data(data)
    if not validation_result['valid']:
        return jsonify({"error": validation_result['errors']}), 400
    
    # Check user's daily listing limit based on subscription
    subscription = Subscription.get_by_user_id(user_id)
    
    # Create new listing
    listing = PickListing(
        id=str(uuid.uuid4()),
        seller_id=user_id,
        title=data['title'],
        description=data['description'],
        price=float(data['price']),
        sport=data['sport'],
        bet_type=data['bet_type'],
        teams=data.get('teams', []),
        odds=data.get('odds'),
        pick_details=data['pick_details'],
        expiration=datetime.utcnow() + timedelta(days=int(data.get('duration_days', 1))),
        created_at=datetime.utcnow(),
        active=True
    )
    
    # Save to database
    listing.save()
    
    # Track this listing for AI performance analysis
    # This would typically call your AI service to monitor the pick
    
    return jsonify({
        "message": "Listing created successfully",
        "listing_id": listing.id,
        "listing": listing.to_dict()
    }), 201

@marketplace_bp.route('/listings/<listing_id>', methods=['PUT'])
@auth_required
def update_listing(listing_id):
    """Update an existing listing (owner only)"""
    user_id = g.user_id
    listing = PickListing.get_by_id(listing_id)
    
    if not listing:
        return jsonify({"error": "Listing not found"}), 404
    
    # Check if user is the owner
    if listing.seller_id != user_id:
        return jsonify({"error": "Unauthorized to modify this listing"}), 403
    
    data = request.json
    
    # Only allow updating specific fields
    updatable_fields = ['title', 'description', 'price', 'active']
    
    for field in updatable_fields:
        if field in data:
            setattr(listing, field, data[field])
    
    # Save changes
    listing.update()
    
    return jsonify({
        "message": "Listing updated successfully",
        "listing": listing.to_dict()
    })

@marketplace_bp.route('/listings/<listing_id>', methods=['DELETE'])
@auth_required
def delete_listing(listing_id):
    """Delete/deactivate a listing (owner only)"""
    user_id = g.user_id
    listing = PickListing.get_by_id(listing_id)
    
    if not listing:
        return jsonify({"error": "Listing not found"}), 404
    
    # Check if user is the owner
    if listing.seller_id != user_id:
        return jsonify({"error": "Unauthorized to delete this listing"}), 403
    
    # Check if listing has been purchased
    if Transaction.has_any_purchases(listing_id):
        # Soft delete - just mark as inactive
        listing.active = False
        listing.update()
        return jsonify({"message": "Listing deactivated successfully"})
    else:
        # Hard delete if no purchases
        listing.delete()
        return jsonify({"message": "Listing deleted successfully"})

@marketplace_bp.route('/buy/<listing_id>', methods=['POST'])
@auth_required
def buy_pick(listing_id):
    """Purchase a pick from the marketplace"""
    user_id = g.user_id
    listing = PickListing.get_by_id(listing_id)
    
    if not listing:
        return jsonify({"error": "Listing not found"}), 404
    
    if not listing.active:
        return jsonify({"error": "This listing is no longer available"}), 400
    
    # Check if user already purchased this listing
    if Transaction.has_user_purchased(user_id, listing_id):
        return jsonify({"error": "You have already purchased this pick"}), 400
    
    # Prevent buying own pick
    if listing.seller_id == user_id:
        return jsonify({"error": "You cannot purchase your own pick"}), 400
    
    # Get payment method from request
    payment_method_id = request.json.get('payment_method_id')
    if not payment_method_id:
        return jsonify({"error": "Payment method required"}), 400
    
    try:
        # Process payment via Stripe Connect
        # Calculate platform fee (10%)
        amount = int(listing.price * 100)  # Convert to cents
        platform_fee = int(amount * PLATFORM_FEE_PERCENT / 100)
        
        payment_result = process_marketplace_payment(
            amount=amount,
            payment_method_id=payment_method_id,
            seller_id=listing.seller_id,
            platform_fee=platform_fee,
            description=f"Purchase: {listing.title}"
        )
        
        if payment_result['success']:
            # Record transaction
            transaction = Transaction(
                id=str(uuid.uuid4()),
                buyer_id=user_id,
                seller_id=listing.seller_id,
                listing_id=listing_id,
                amount=listing.price,
                platform_fee_percent=PLATFORM_FEE_PERCENT,
                payment_id=payment_result['payment_id'],
                status="completed",
                created_at=datetime.utcnow()
            )
            transaction.save()
            
            # Return success response with full pick details
            return jsonify({
                "message": "Purchase successful",
                "transaction_id": transaction.id,
                "pick_details": listing.get_full_details()
            })
        else:
            return jsonify({
                "error": "Payment failed",
                "details": payment_result['error']
            }), 400
            
    except Exception as e:
        return jsonify({
            "error": "An error occurred during payment processing",
            "details": str(e)
        }), 500

@marketplace_bp.route('/my/listings', methods=['GET'])
@auth_required
@premium_required
def get_my_listings():
    """Get all listings created by the current user"""
    user_id = g.user_id
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
    
    # Build filters
    filters = {'seller_id': user_id}
    if not include_inactive:
        filters['active'] = True
    
    # Get listings
    listings, total = PickListing.get_listings(
        page=page,
        per_page=per_page,
        filters=filters,
        sort_by='created_at',
        sort_dir='desc'
    )
    
    # Get performance metrics for each listing
    listings_with_performance = []
    for listing in listings:
        listing_dict = listing.to_dict()
        
        # Add performance metrics
        transactions_count = Transaction.count_by_listing(listing.id)
        revenue = Transaction.get_revenue_by_listing(listing.id)
        
        listing_dict['performance'] = {
            'purchases': transactions_count,
            'revenue': revenue,
            'success_rate': listing.get_success_rate()  # Win rate if bet completed
        }
        
        listings_with_performance.append(listing_dict)
    
    return jsonify({
        "listings": listings_with_performance,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page
        }
    })

@marketplace_bp.route('/my/purchases', methods=['GET'])
@auth_required
def get_my_purchases():
    """Get all picks purchased by the current user"""
    user_id = g.user_id
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    # Get transactions
    transactions, total = Transaction.get_user_purchases(
        user_id=user_id,
        page=page,
        per_page=per_page
    )
    
    # Get full details for each purchased pick
    purchases = []
    for transaction in transactions:
        listing = PickListing.get_by_id(transaction.listing_id)
        if listing:
            purchase_data = {
                "transaction_id": transaction.id,
                "purchase_date": transaction.created_at.isoformat(),
                "amount": transaction.amount,
                "listing": listing.to_dict(),
                "full_details": listing.get_full_details(),
                "result": listing.get_result()  # Win/Loss/Pending
            }
            purchases.append(purchase_data)
    
    return jsonify({
        "purchases": purchases,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page
        }
    })

@marketplace_bp.route('/sales', methods=['GET'])
@auth_required
@premium_required
def get_sales_dashboard():
    """Get sales performance dashboard for the seller"""
    user_id = g.user_id
    
    # Get basic sales metrics
    total_sales = Transaction.count_by_seller(user_id)
    total_revenue = Transaction.get_revenue_by_seller(user_id)
    platform_fees = Transaction.get_platform_fees_by_seller(user_id)
    net_earnings = total_revenue - platform_fees
    
    # Get recent sales
    recent_sales, _ = Transaction.get_seller_transactions(
        seller_id=user_id,
        page=1,
        per_page=10
    )
    
    # Get pick performance stats
    win_rate = User.get_win_rate_for_picks(user_id)
    best_performing_pick = PickListing.get_best_performing(user_id)
    
    return jsonify({
        "sales_summary": {
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "platform_fees": platform_fees,
            "net_earnings": net_earnings
        },
        "performance": {
            "win_rate": win_rate,
            "best_performing_pick": best_performing_pick.to_dict() if best_performing_pick else None
        },
        "recent_sales": [
            {
                "transaction_id": sale.id,
                "listing_id": sale.listing_id,
                "listing_title": PickListing.get_by_id(sale.listing_id).title if PickListing.get_by_id(sale.listing_id) else "Deleted Pick",
                "amount": sale.amount,
                "date": sale.created_at.isoformat()
            } for sale in recent_sales
        ]
    })

# Admin endpoints
@marketplace_bp.route('/admin/listings', methods=['GET'])
@auth_required
@admin_required
def admin_get_listings():
    """Admin endpoint to get all marketplace listings"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    status = request.args.get('status')  # active, inactive, all
    
    filters = {}
    if status == 'active':
        filters['active'] = True
    elif status == 'inactive':
        filters['active'] = False
    
    listings, total = PickListing.get_listings(
        page=page, 
        per_page=per_page, 
        filters=filters,
        sort_by='created_at',
        sort_dir='desc'
    )
    
    return jsonify({
        "listings": [listing.to_dict() for listing in listings],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page
        }
    })

@marketplace_bp.route('/admin/transactions', methods=['GET'])
@auth_required
@admin_required
def admin_get_transactions():
    """Admin endpoint to get all marketplace transactions"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    transactions, total = Transaction.get_all_transactions(
        page=page,
        per_page=per_page
    )
    
    return jsonify({
        "transactions": [transaction.to_dict() for transaction in transactions],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page
        },
        "summary": {
            "total_revenue": Transaction.get_total_revenue(),
            "platform_fees": Transaction.get_total_platform_fees()
        }
    })