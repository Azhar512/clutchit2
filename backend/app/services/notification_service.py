import firebase_admin
from firebase_admin import messaging
import json

def send_push_notification(token, title, body, data=None):
    """
    Send push notification to a specific device
    """
    if data is None:
        data = {}
        
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        data=data,
        token=token
    )
    
    response = messaging.send(message)
    return response

def send_hedging_alert(user_tokens, bet_id, game_info, recommendation):
    """
    Send hedging recommendation alert
    """
    title = "Hedging Opportunity!"
    body = f"Consider hedging your bet on {game_info['teams']}. {recommendation['short_message']}"
    
    data = {
        'type': 'hedge_alert',
        'bet_id': str(bet_id),
        'teams': game_info['teams'],
        'recommendation': json.dumps(recommendation)
    }
    
    for token in user_tokens:
        send_push_notification(token, title, body, data)
        
def send_close_to_winning_alert(user_tokens, bet_id, game_info):
    """
    Send alert when a bet is close to winning
    """
    title = "Almost There!"
    body = f"Your bet on {game_info['teams']} is close to winning!"
    
    data = {
        'type': 'close_to_winning',
        'bet_id': str(bet_id),
        'teams': game_info['teams'],
        'game_status': game_info['status']
    }
    
    for token in user_tokens:
        send_push_notification(token, title, body, data)