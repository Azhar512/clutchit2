import unittest
from app import create_app
from models import db
from models.bankroll import Bankroll, BankrollHistory, WagerRecommendation
from services.bankroll_service import BankrollService

class BankrollServiceTestCase(unittest.TestCase):
    """Tests for the bankroll service."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up after tests."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_kelly_criterion(self):
        """Test Kelly Criterion calculation."""
        with self.app.app_context():
            # Test various scenarios
            # Win probability = 0.6, odds = 2.0 (even money)
            kelly = BankrollService.kelly_criterion(0.6, 2.0)
            self.assertAlmostEqual(kelly, 0.2, places=2)
            
            # Win probability = 0.5, odds = 2.0 (break-even)
            kelly = BankrollService.kelly_criterion(0.5, 2.0)
            self.assertAlmostEqual(kelly, 0.0, places=2)
            
            # Win probability = 0.7, odds = 1.5 (favorite)
            kelly = BankrollService.kelly_criterion(0.7, 1.5)
            self.assertAlmostEqual(kelly, 0.4, places=2)
    
    def test_risk_factor(self):
        """Test risk factor mapping."""
        with self.app.app_context():
            self.assertEqual(BankrollService.get_risk_factor('low'), 0.25)
            self.assertEqual(BankrollService.get_risk_factor('medium'), 0.5)
            self.assertEqual(BankrollService.get_risk_factor('high'), 1.0)
            self.assertEqual(BankrollService.get_risk_factor('invalid'), 0.5)  # Default
    
    def test_update_bankroll(self):
        """Test bankroll update functionality."""
        with self.app.app_context():
            # Create a test user
            from models.user import User
            user = User(username='testuser', email='test@example.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            
            # Initial bankroll creation
            result = BankrollService.update_bankroll(
                user_id=user.id,
                current_amount=1000.0,
                target_profit=500.0,
                risk_profile='medium'
            )
            
            # Check bankroll was created
            bankroll = Bankroll.query.filter_by(user_id=user.id).first()
            self.assertIsNotNone(bankroll)
            self.assertEqual(bankroll.current_amount, 1000.0)
            self.assertEqual(bankroll.target_profit, 500.0)
            self.assertEqual(bankroll.risk_profile, 'medium')
            
            # Update bankroll
            result = BankrollService.update_bankroll(
                user_id=user.id,
                current_amount=1200.0,
                target_profit=600.0,
                risk_profile='high'
            )
            
            # Verify update
            bankroll = Bankroll.query.filter_by(user_id=user.id).first()
            self.assertEqual(bankroll.current_amount, 1200.0)
            self.assertEqual(bankroll.target_profit, 600.0)
            self.assertEqual(bankroll.risk_profile, 'high')
            
            # Check history record was created
            history = BankrollHistory.query.filter_by(bankroll_id=bankroll.id).first()
            self.assertIsNotNone(history)
            self.assertEqual(history.amount, 1000.0)  # Original amount