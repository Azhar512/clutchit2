from flask import jsonify
from  app.models.marketplace import Pick, FeaturedPick, Category
from app.models.user import User
from  app.models.subscription import Subscription
from sqlalchemy import desc
import datetime

class MarketplaceService:
    def __init__(self, db):
        self.db = db

    def get_featured_picks(self):
        """Get all featured picks sorted by creation date"""
        try:
            featured_picks = FeaturedPick.query.filter_by(active=True).order_by(desc(FeaturedPick.created_at)).limit(6).all()
            return [pick.to_dict() for pick in featured_picks]
        except Exception as e:
            print(f"Error getting featured picks: {e}")
            return []

    def get_clutch_picks(self, limit=8):
        """Get premium/clutch picks"""
        try:
            thirty_days_ago = datetime.datetime.now() - datetime.timedelta(days=30)
            
            picks = Pick.query.filter(
                Pick.created_at >= thirty_days_ago,
                Pick.active == True
            ).order_by(desc(Pick.sales), desc(Pick.rating)).limit(limit).all()
            
            return [pick.to_dict() for pick in picks]
        except Exception as e:
            print(f"Error getting clutch picks: {e}")
            return []

    def get_trending_categories(self):
        """Get trending categories based on recent activity"""
        try:
            categories = Category.query.filter_by(active=True).order_by(desc(Category.pick_count)).limit(4).all()
            return [category.to_dict() for category in categories]
        except Exception as e:
            print(f"Error getting trending categories: {e}")
            return ["NBA", "NFL", "MLB", "UFC"]  

    def purchase_pick(self, user_id, pick_id):
        """Process a pick purchase"""
        try:
            user = User.query.get(user_id)
            pick = Pick.query.get(pick_id)
            
            if not user or not pick:
                return {"success": False, "message": "User or pick not found"}
                
            subscription = Subscription.query.filter_by(user_id=user_id, active=True).first()
            
            if not subscription or subscription.tier < pick.required_tier:
                pass
                
            user.purchased_picks.append(pick)
            
            pick.sales += 1
            
            self.db.session.commit()
            
            return {"success": True, "message": "Pick purchased successfully", "pick": pick.to_dict()}
        except Exception as e:
            self.db.session.rollback()
            print(f"Error purchasing pick: {e}")
            return {"success": False, "message": "Error processing purchase"}