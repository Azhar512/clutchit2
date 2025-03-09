import stripe

# Set your test secret key
stripe.api_key = "sk_test_51QrvvHBS5C3Ve8QARkCOO2Gi0aeDRIVCgKzNDs8puQ2PVcbce1VkjtUUYSuJMoejmMwRhmcniUGy8WrBtrO3kR8b00PJRAp8lx"  # Replace with your full key

try:
    account = stripe.Account.retrieve()
    print("✅ Stripe API Key is valid!")
    print("🔹 Account ID:", account.id)
except stripe.error.AuthenticationError:
    print("❌ Invalid API Key: Authentication failed.")
except Exception as e:
    print("❌ Error:", e)
