from flask import Blueprint, request, jsonify, current_app, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionType, SUBSCRIPTION_PRICE_MAP
from app import db
from datetime import datetime, timedelta
import os
import stripe
import json

subscription_bp = Blueprint('subscription', __name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@subscription_bp.route('/', methods=['GET'])
@jwt_required()
def get_subscription():
    current_user_id = get_jwt_identity()
    subscription = Subscription.query.filter_by(user_id=current_user_id).first()
    
    if not subscription:
        return jsonify({"error": "No active subscription found"}), 404
    
    return jsonify(subscription.to_dict()), 200

@subscription_bp.route('/create', methods=['POST'])
@jwt_required()
def create_subscription():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    
    if 'subscription_type' not in data:
        return jsonify({"error": "Missing subscription_type parameter"}), 400
    
    # Convert the incoming subscription_type to uppercase to match enum values
    subscription_type_str = data['subscription_type'].upper()
    
    # Map from string to actual enum values
    subscription_map = {
        "BASIC": SubscriptionType.BASIC,
        "PREMIUM": SubscriptionType.PREMIUM, 
        "UNLIMITED": SubscriptionType.UNLIMITED
    }
    
    if subscription_type_str not in subscription_map:
        return jsonify({"error": "Invalid subscription type"}), 400
    
    subscription_type = subscription_map[subscription_type_str]
    
    # Create or get Stripe customer
    if not user.stripe_customer_id:
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.username}",
                metadata={
                    'user_id': str(user.id)
                }
            )
            user.stripe_customer_id = customer.id
            db.session.commit()
        except stripe.error.StripeError as e:
            return jsonify({"error": f"Stripe error: {str(e)}"}), 400
    
    # Create Stripe subscription with trial
    try:
        stripe_subscription = stripe.Subscription.create(
            customer=user.stripe_customer_id,
            items=[{
                'price': SUBSCRIPTION_PRICE_MAP[subscription_type]
            }],
            trial_period_days=3,
            metadata={
                'user_id': str(user.id),
                'subscription_type': subscription_type
            }
        )
        
        # Set end date based on trial or current period
        if stripe_subscription.trial_end:
            end_date = datetime.fromtimestamp(stripe_subscription.trial_end)
            trial_end = datetime.fromtimestamp(stripe_subscription.trial_end)
        else:
            end_date = datetime.fromtimestamp(stripe_subscription.current_period_end)
            trial_end = None
        
        new_subscription = Subscription(
            user_id=current_user_id,
            subscription_type=subscription_type,
            start_date=datetime.utcnow(),
            end_date=end_date,
            is_active=True,
            stripe_customer_id=user.stripe_customer_id,
            stripe_subscription_id=stripe_subscription.id,
            stripe_status=stripe_subscription.status,
            trial_end=trial_end
        )
        
        db.session.add(new_subscription)
        db.session.commit()
        
        return jsonify({
            "message": "Subscription created successfully",
            "subscription": new_subscription.to_dict()
        }), 201
    
    except stripe.error.StripeError as e:
        return jsonify({"error": f"Stripe error: {str(e)}"}), 400

@subscription_bp.route('/checkout-session', methods=['POST'])
@jwt_required()
def create_checkout_session():
    """Create a Stripe Checkout session for subscription payments"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    
    if 'subscription_type' not in data:
        return jsonify({"error": "Missing subscription_type parameter"}), 400
    
    # Convert the incoming subscription_type to uppercase to match enum values
    subscription_type_str = data['subscription_type'].upper()
    
    # Map from string to actual enum values
    subscription_map = {
        "BASIC": SubscriptionType.BASIC,
        "PREMIUM": SubscriptionType.PREMIUM, 
        "UNLIMITED": SubscriptionType.UNLIMITED
    }
    
    if subscription_type_str not in subscription_map:
        return jsonify({"error": "Invalid subscription type"}), 400
    
    subscription_type = subscription_map[subscription_type_str]
    
    # Create checkout session
    try:
        success_url = request.host_url + 'subscription/success?session_id={CHECKOUT_SESSION_ID}'
        cancel_url = request.host_url + 'subscription/cancel'
        
        checkout_session = stripe.checkout.Session.create(
            customer_email=user.email if not user.stripe_customer_id else None,
            customer=user.stripe_customer_id if user.stripe_customer_id else None,
            payment_method_types=['card'],
            line_items=[{
                'price': SUBSCRIPTION_PRICE_MAP[subscription_type],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'user_id': str(user.id),
                'subscription_type': subscription_type
            }
        )
        
        return jsonify({
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({"error": f"Stripe error: {str(e)}"}), 400

@subscription_bp.route('/cancel', methods=['POST'])
@jwt_required()
def cancel_subscription():
    current_user_id = get_jwt_identity()
    subscription = Subscription.query.filter_by(user_id=current_user_id, is_active=True).first()
    
    if not subscription:
        return jsonify({"error": "No active subscription found"}), 404
    
    if subscription.stripe_subscription_id:
        try:
            # Cancel at period end to avoid immediate cancellation
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )
        except stripe.error.StripeError as e:
            return jsonify({"error": f"Stripe error: {str(e)}"}), 400
    
    subscription.is_active = False
    db.session.commit()
    
    return jsonify({
        "message": "Subscription cancelled successfully"
    }), 200

@subscription_bp.route('/upgrade', methods=['POST'])
@jwt_required()
def upgrade_subscription():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    
    if 'subscription_type' not in data:
        return jsonify({"error": "Missing subscription_type parameter"}), 400
    
    # Convert the incoming subscription_type to uppercase to match enum values
    subscription_type_str = data['subscription_type'].upper()
    
    # Map from string to actual enum values
    subscription_map = {
        "BASIC": SubscriptionType.BASIC,
        "PREMIUM": SubscriptionType.PREMIUM, 
        "UNLIMITED": SubscriptionType.UNLIMITED
    }
    
    if subscription_type_str not in subscription_map:
        return jsonify({"error": "Invalid subscription type"}), 400
    
    subscription_type = subscription_map[subscription_type_str]
    
    subscription = Subscription.query.filter_by(user_id=current_user_id, is_active=True).first()
    
    if not subscription:
        return jsonify({"error": "No active subscription found"}), 404
    
    # If subscription exists in Stripe, update it
    if subscription.stripe_subscription_id:
        try:
            # Get the subscription from Stripe
            stripe_sub = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
            
            # Get the subscription item ID (usually the first item)
            item_id = stripe_sub['items']['data'][0].id
            
            # Update the subscription item with the new price
            stripe.SubscriptionItem.modify(
                item_id,
                price=SUBSCRIPTION_PRICE_MAP[subscription_type],
            )
            
            # Update metadata
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                metadata={
                    'user_id': str(user.id),
                    'subscription_type': subscription_type
                }
            )
            
            # Get updated subscription
            updated_stripe_sub = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
            
            # Update the local subscription
            subscription.subscription_type = subscription_type
            subscription.end_date = datetime.fromtimestamp(updated_stripe_sub.current_period_end)
            subscription.update_from_stripe()
            
            db.session.commit()
            
            return jsonify({
                "message": "Subscription upgraded successfully",
                "subscription": subscription.to_dict()
            }), 200
            
        except stripe.error.StripeError as e:
            return jsonify({"error": f"Stripe error: {str(e)}"}), 400
    else:
        # Just update the local record if not using Stripe
        subscription.subscription_type = subscription_type
        db.session.commit()
        
        return jsonify({
            "message": "Subscription upgraded successfully",
            "subscription": subscription.to_dict()
        }), 200

@subscription_bp.route('/webhook', methods=['POST'])
def webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_completed(session)
    elif event['type'] == 'customer.subscription.created':
        subscription = event['data']['object']
        handle_subscription_created(subscription)
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        handle_subscription_updated(subscription)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)
    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        handle_payment_failed(invoice)
    
    return jsonify({'status': 'success'}), 200

def handle_checkout_completed(session):
    """Process completed checkout session"""
    user_id = session.get('metadata', {}).get('user_id')
    if not user_id:
        current_app.logger.error("No user_id in checkout session metadata")
        return
    
    user = User.query.get(user_id)
    if not user:
        current_app.logger.error(f"User not found: {user_id}")
        return
    
    # Update or create Stripe customer ID
    if not user.stripe_customer_id and session.get('customer'):
        user.stripe_customer_id = session['customer']
        db.session.commit()

def handle_subscription_created(subscription_data):
    """Handle new subscription creation"""
    user_id = subscription_data.get('metadata', {}).get('user_id')
    if not user_id:
        current_app.logger.error("No user_id in subscription metadata")
        return
    
    user = User.query.get(user_id)
    if not user:
        current_app.logger.error(f"User not found: {user_id}")
        return
    
    subscription_type = subscription_data.get('metadata', {}).get('subscription_type', SubscriptionType.BASIC)
    
    # Set end date based on trial or current period
    if subscription_data.get('trial_end'):
        end_date = datetime.fromtimestamp(subscription_data['trial_end'])
        trial_end = datetime.fromtimestamp(subscription_data['trial_end'])
    else:
        end_date = datetime.fromtimestamp(subscription_data['current_period_end'])
        trial_end = None
    
    # Check if subscription already exists
    existing_sub = Subscription.query.filter_by(stripe_subscription_id=subscription_data['id']).first()
    if existing_sub:
        # Update existing subscription
        existing_sub.stripe_status = subscription_data['status']
        existing_sub.end_date = end_date
        existing_sub.trial_end = trial_end
        existing_sub.is_active = subscription_data['status'] in ['active', 'trialing']
    else:
        # Create new subscription record
        new_subscription = Subscription(
            user_id=user.id,
            subscription_type=subscription_type,
            start_date=datetime.utcnow(),
            end_date=end_date,
            is_active=subscription_data['status'] in ['active', 'trialing'],
            stripe_customer_id=subscription_data['customer'],
            stripe_subscription_id=subscription_data['id'],
            stripe_status=subscription_data['status'],
            trial_end=trial_end
        )
        db.session.add(new_subscription)
    
    db.session.commit()

def handle_subscription_updated(subscription_data):
    """Handle subscription updates"""
    # Find subscription by Stripe ID
    subscription = Subscription.query.filter_by(stripe_subscription_id=subscription_data['id']).first()
    if not subscription:
        current_app.logger.error(f"Subscription not found: {subscription_data['id']}")
        return
    
    # Update subscription details
    subscription.stripe_status = subscription_data['status']
    
    if subscription_data.get('trial_end'):
        subscription.trial_end = datetime.fromtimestamp(subscription_data['trial_end'])
    
    subscription.end_date = datetime.fromtimestamp(subscription_data['current_period_end'])
    subscription.is_active = subscription_data['status'] in ['active', 'trialing']
    
    # Check if subscription type changed
    subscription_type = subscription_data.get('metadata', {}).get('subscription_type')
    if subscription_type and subscription_type in [SubscriptionType.BASIC, SubscriptionType.PREMIUM, SubscriptionType.UNLIMITED]:
        subscription.subscription_type = subscription_type
    
    db.session.commit()

def handle_subscription_deleted(subscription_data):
    """Handle subscription cancellation/deletion"""
    subscription = Subscription.query.filter_by(stripe_subscription_id=subscription_data['id']).first()
    if not subscription:
        current_app.logger.error(f"Subscription not found: {subscription_data['id']}")
        return
    
    subscription.is_active = False
    subscription.stripe_status = subscription_data['status']
    db.session.commit()

def handle_payment_failed(invoice):
    """Handle failed payment"""
    subscription_id = invoice.get('subscription')
    if not subscription_id:
        return
    
    subscription = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
    if not subscription:
        current_app.logger.error(f"Subscription not found: {subscription_id}")
        return
    
    # Update subscription status
    subscription.stripe_status = 'past_due'
    db.session.commit()