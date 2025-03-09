import numpy as np
from datetime import datetime, timedelta
from app.models.bankroll import Bankroll, BankrollHistory, WagerRecommendation
from app.models import db
from app.services.bet_service import get_bets_with_ev

class BankrollService:
    """Service class for bankroll management calculations."""
    
    @staticmethod
    def kelly_criterion(win_probability, odds):
        """
        Calculate Kelly Criterion for optimal bet size.
        
        Args:
            win_probability (float): Probability of winning (0.0 to 1.0)
            odds (float): Decimal odds (e.g., 2.5 for +150 American odds)
            
        Returns:
            float: Kelly stake as a fraction of bankroll
        """
        if win_probability <= 0 or win_probability >= 1:
            return 0
            
        # Kelly formula: f* = (bp - q) / b
        # where f* is stake fraction, b is odds-1, p is win probability, q is loss probability
        b = odds - 1
        q = 1 - win_probability
        
        kelly = (b * win_probability - q) / b
        
        # Clamp between 0 and 1
        return max(0, min(kelly, 1))
    
    @staticmethod
    def get_risk_factor(risk_profile):
        """
        Get multiplier based on user's risk profile.
        
        Args:
            risk_profile (str): 'low', 'medium', or 'high'
            
        Returns:
            float: Risk factor multiplier for Kelly criterion
        """
        risk_factors = {
            'low': 0.25,     # Conservative: 1/4 Kelly
            'medium': 0.5,   # Moderate: 1/2 Kelly
            'high': 1.0      # Aggressive: Full Kelly
        }
        return risk_factors.get(risk_profile, 0.5)
    
    @staticmethod
    def calculate_wager_recommendations(user_id, days_projection=30):
        """
        Calculate recommended wagers based on user's bankroll and target.
        
        Args:
            user_id (int): User ID
            days_projection (int): Number of days to project into the future
            
        Returns:
            dict: Recommended wagers and projection data
        """
        # Get user's bankroll info
        bankroll = Bankroll.query.filter_by(user_id=user_id).first()
        if not bankroll:
            return {"error": "Bankroll not set up for this user"}
        
        # Get top EV bets for the user based on subscription tier
        bets_with_ev = get_bets_with_ev(user_id)
        
        # Initialize results
        daily_wagers = []
        cumulative_profit = 0
        current_bankroll = bankroll.current_amount
        risk_factor = BankrollService.get_risk_factor(bankroll.risk_profile)
        
        # Get today's date
        today = datetime.now().date()
        
        # Clear existing future recommendations
        WagerRecommendation.query.filter(
            WagerRecommendation.bankroll_id == bankroll.id,
            WagerRecommendation.date >= today
        ).delete()
        
        # Calculate daily recommendations
        for day in range(days_projection):
            projection_date = today + timedelta(days=day)
            
            # If we have specific bets with EV for this day, use them
            # Otherwise use average EV from available bets
            if day < len(bets_with_ev):
                bet = bets_with_ev[day]
                win_prob = (bet['implied_probability'] + 0.5) / 2  # Adjusted for EV
                odds = bet['odds']
                bet_id = bet['id']
            else:
                # Use average values from available bets if we've run out of specific bets
                avg_win_prob = sum([b['implied_probability'] for b in bets_with_ev]) / len(bets_with_ev) if bets_with_ev else 0.55
                avg_odds = sum([b['odds'] for b in bets_with_ev]) / len(bets_with_ev) if bets_with_ev else 2.0
                win_prob = avg_win_prob
                odds = avg_odds
                bet_id = None
            
            # Calculate Kelly stake and adjust by risk preference
            kelly_stake = BankrollService.kelly_criterion(win_prob, odds)
            recommended_stake = kelly_stake * risk_factor
            
            # Calculate wager amount for today
            wager_amount = current_bankroll * recommended_stake
            
            # Simulate expected daily profit
            expected_profit = wager_amount * (odds - 1) * win_prob - wager_amount * (1 - win_prob)
            
            # Create recommendation record
            recommendation = WagerRecommendation(
                bankroll_id=bankroll.id,
                date=projection_date,
                recommended_wager=round(wager_amount, 2),
                expected_profit=round(expected_profit, 2),
                bet_id=bet_id
            )
            db.session.add(recommendation)
            
            # Update running totals for projection
            cumulative_profit += expected_profit
            current_bankroll += expected_profit
            
            # Store for response
            daily_wagers.append({
                'date': projection_date.isoformat(),
                'recommended_wager': round(wager_amount, 2),
                'expected_profit': round(expected_profit, 2),
                'cumulative_profit': round(cumulative_profit, 2),
                'projected_bankroll': round(bankroll.current_amount + cumulative_profit, 2),
            })
            
            # Check if target has been reached
            if cumulative_profit >= bankroll.target_profit:
                break
        
        db.session.commit()
        
        # Calculate estimated days to target
        daily_avg_profit = cumulative_profit / len(daily_wagers) if daily_wagers else 0
        days_to_target = int(bankroll.target_profit / daily_avg_profit) if daily_avg_profit > 0 else float('inf')
        
        return {
            'current_bankroll': bankroll.current_amount,
            'target_profit': bankroll.target_profit,
            'risk_profile': bankroll.risk_profile,
            'daily_wagers': daily_wagers,
            'estimated_days_to_target': days_to_target,
            'cumulative_profit_30_days': round(cumulative_profit, 2)
        }
    
    @staticmethod
    def update_bankroll(user_id, current_amount, target_profit, risk_profile):
        """
        Create or update a user's bankroll settings.
        
        Args:
            user_id (int): User ID
            current_amount (float): Current bankroll amount
            target_profit (float): Target profit amount
            risk_profile (str): Risk profile ('low', 'medium', 'high')
            
        Returns:
            dict: Updated bankroll information
        """
        # Validate input
        if current_amount <= 0:
            return {"error": "Current amount must be positive"}
        if target_profit <= 0:
            return {"error": "Target profit must be positive"}
        if risk_profile not in ['low', 'medium', 'high']:
            return {"error": "Risk profile must be 'low', 'medium', or 'high'"}
        
        # Get existing bankroll or create new one
        bankroll = Bankroll.query.filter_by(user_id=user_id).first()
        if bankroll:
            # Create history record before updating
            history = BankrollHistory(
                bankroll_id=bankroll.id,
                amount=bankroll.current_amount,
                date=datetime.now().date()
            )
            db.session.add(history)
            
            # Update existing bankroll
            bankroll.current_amount = current_amount
            bankroll.target_profit = target_profit
            bankroll.risk_profile = risk_profile
        else:
            # Create new bankroll
            bankroll = Bankroll(
                user_id=user_id,
                current_amount=current_amount,
                target_profit=target_profit,
                risk_profile=risk_profile
            )
            db.session.add(bankroll)
        
        db.session.commit()
        
        # Return updated data with recommendations
        recommendations = BankrollService.calculate_wager_recommendations(user_id)
        return {
            'bankroll': bankroll.to_dict(),
            'recommendations': recommendations
        }