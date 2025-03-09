# File: app/scripts/init_faq_data.py

from app.db import db
from app.models.faq import FAQCategory, FAQ

def init_faq_categories():
    """Initialize FAQ categories."""
    categories = [
        {
            'title': 'Getting Started',
            'icon_name': 'Book',
            'description': 'Learn the basics of using Clutch It app'
        },
        {
            'title': 'Account & Billing',
            'icon_name': 'CreditCard',
            'description': 'Subscription plans, payments, and account management'
        },
        {
            'title': 'Uploading Bets',
            'icon_name': 'Upload',
            'description': 'How to upload and manage your bets'
        },
        {
            'title': 'Marketplace',
            'icon_name': 'ShoppingBag',
            'description': 'Buying and selling picks in the marketplace'
        },
        {
            'title': 'Technical Issues',
            'icon_name': 'Zap',
            'description': 'Common problems and troubleshooting'
        }
    ]
    
    for i, category_data in enumerate(categories):
        category = FAQCategory(
            title=category_data['title'],
            icon_name=category_data['icon_name'],
            description=category_data['description'],
            order=i
        )
        db.session.add(category)
    
    db.session.commit()
    print("FAQ categories initialized successfully.")

def init_faq_questions():
    """Initialize FAQ questions."""
    # Get category IDs
    getting_started = FAQCategory.query.filter_by(title='Getting Started').first()
    account_billing = FAQCategory.query.filter_by(title='Account & Billing').first()
    uploading = FAQCategory.query.filter_by(title='Uploading Bets').first()
    marketplace = FAQCategory.query.filter_by(title='Marketplace').first()
    technical = FAQCategory.query.filter_by(title='Technical Issues').first()
    
    faqs = [
        # Getting Started
        {
            'category_id': getting_started.id,
            'question': 'How do I get started with Clutch It?',
            'answer': 'To get started with Clutch It, download our app from the App Store or Google Play Store, create an account, and choose a subscription plan. We offer a 3-day free trial for all new users. Once registered, you can start uploading bets, access AI predictions, and explore the marketplace.'
        },
        {
            'category_id': getting_started.id,
            'question': 'What features are available on Clutch It?',
            'answer': 'Clutch It offers several key features:\n\n- AI-powered bet analysis and predictions\n- Expected Value (EV) calculations\n- Bankroll management recommendations\n- Marketplace for buying and selling picks\n- Real-time notifications for optimal betting moments\n- Leaderboard to track performance\n\nFeature access depends on your subscription plan.'
        },
        {
            'category_id': getting_started.id,
            'question': 'How accurate are the AI predictions?',
            'answer': 'Our AI predictions are based on sophisticated machine learning models trained on millions of bets. While no prediction system is perfect, our AI continuously improves through feedback and real-world results. We track prediction accuracy on our platform and typically achieve better-than-market results. Remember that sports betting always involves risk.'
        },
        
        # Account & Billing
        {
            'category_id': account_billing.id,
            'question': 'What subscription plans do you offer?',
            'answer': 'We offer three subscription plans:\n\n1. Basic ($10/month): 10 uploads per day, access to 10 top picks daily, ability to buy picks.\n2. Premium ($20/month): Unlimited uploads, access to 20 top picks daily, ability to buy and sell picks.\n3. Unlimited ($40/month): Unlimited uploads, unlimited access to all picks, and full marketplace functionality.\n\nAll new users receive a 3-day free trial with full access.'
        },
        {
            'category_id': account_billing.id,
            'question': 'How do I cancel my subscription?',
            'answer': 'To cancel your subscription, go to the Account/Profile section, select Subscription Management, and click on Cancel Subscription. Your subscription will remain active until the end of your current billing cycle. You can reactivate your subscription at any time.'
        },
        {
            'category_id': account_billing.id,
            'question': 'How do I withdraw my earnings?',
            'answer': 'You can withdraw your marketplace earnings by going to Account/Profile > Earnings > Withdraw. We process withdrawals through the payment method on file. The minimum withdrawal amount is $20, and processing usually takes 2-3 business days. Note that a 10% platform fee is applied to all marketplace transactions.'
        },
        
        # Uploading Bets
        {
            'category_id': uploading.id,
            'question': 'How do I upload a bet?',
            'answer': 'To upload a bet, navigate to the Upload Bet page and choose one of two methods:\n\n1. Image Upload: Take a screenshot of your bet slip and upload it. Our system will use OCR to extract the bet details.\n2. Manual Entry: Enter the details manually using our form.\n\nOnce submitted, our AI will analyze your bet and provide predictions and EV calculations.'
        },
        {
            'category_id': uploading.id,
            'question': 'What bet types are supported?',
            'answer': 'Clutch It supports most common bet types including:\n\n- Money Line\n- Point Spreads\n- Over/Under (Totals)\n- Props\n- Parlays (including mixed-sport parlays)\n- Teasers\n- Live Bets\n\nOur system automatically categorizes your bets by type and sport.'
        }
        
        # Marketplace
        {
            'category_id': marketplace.id,
            'question': 'Can I become a Clutch Pick seller?',
            'answer': 'Yes, Premium and Unlimited subscribers can sell picks on our marketplace. To become a seller:\n\n1. Upgrade to a Premium or Unlimited subscription\n2. Go to Marketplace > Become a Seller\n3. Complete your seller profile\n4. Start listing your picks\n\nYou'll earn 90% of each sale, with 10% going to the platform as a commission.'
        },
        {
            'category_id': marketplace.id,
            'question': 'How is the marketplace regulated?',
            'answer': 'We maintain marketplace quality through several measures:\n\n- Seller performance tracking\n- User reviews and ratings\n- Automated detection of suspicious activity\n- Manual review by our team\n\nSellers with consistently poor performance may be temporarily suspended or permanently removed from the marketplace.'
        },
        
        # Technical Issues
        {
            'category_id': technical.id,
            'question': 'The app is running slowly. What should I do?',
            'answer': 'If you experience slow performance:\n\n1. Ensure your app is updated to the latest version\n2. Close other apps running in the background\n3. Check your internet connection\n4. Restart the app\n5. If issues persist, try reinstalling the app\n\nIf none of these steps work, please contact our support team with details about your device and the issues you\'re experiencing.'
        },
        {
            'category_id': technical.id,
            'question': 'My bet image upload failed. What should I do?',
            'answer': 'If your bet image upload fails:\n\n1. Ensure the image is clear and well-lit\n2. Try cropping the image to include only the bet slip\n3. Check that you\'re connected to the internet\n4. Retry the upload\n\nIf the issue persists, you can manually enter the bet details or contact our support team for assistance.'
        }
    ]
    
    for faq_data in faqs:
        faq = FAQ(
            category_id=faq_data['category_id'],
            question=faq_data['question'],
            answer=faq_data['answer']
        )
        db.session.add(faq)
    
    db.session.commit()
    print("FAQ questions initialized successfully.")

def run():
    """Run the initialization script."""
    print("Initializing FAQ data...")
    
    # Check if categories already exist
    existing_categories = FAQCategory.query.count()
    if existing_categories == 0:
        init_faq_categories()
    else:
        print(f"Found {existing_categories} existing categories. Skipping category initialization.")
    
    # Check if FAQs already exist
    existing_faqs = FAQ.query.count()
    if existing_faqs == 0:
        init_faq_questions()
    else:
        print(f"Found {existing_faqs} existing FAQs. Skipping FAQ initialization.")
    
    print("FAQ data initialization complete.")

if __name__ == "__main__":
    run()