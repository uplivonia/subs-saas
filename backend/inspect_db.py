from app.db.session import SessionLocal
from app.models.payment import Payment
from app.models.subscription import Subscription
from app.models.plan import SubscriptionPlan
from app.models.project import Project

def show_payments(db):
    print("\n=== LAST PAYMENTS ===")
    payments = db.query(Payment).order_by(Payment.id.desc()).limit(5).all()
    if not payments:
        print("❌ No payments found.")
        return
    
    for p in payments:
        print(f"""
ID: {p.id}
Telegram ID: {p.telegram_id}
Plan ID: {p.plan_id}
Project ID: {p.project_id}
Amount: {p.amount}
Currency: {p.currency}
Status: {p.status}
Stripe Session: {p.stripe_session_id}
Created: {p.created_at}
--------------------------
        """)

def show_subscriptions(db):
    print("\n=== LAST SUBSCRIPTIONS ===")
    subs = db.query(Subscription).order_by(Subscription.id.desc()).limit(5).all()
    if not subs:
        print("❌ No subscriptions found.")
        return
    
    for s in subs:
        plan = db.query(SubscriptionPlan).filter_by(id=s.plan_id).first()
        project = db.query(Project).filter_by(id=s.project_id).first()

        print(f"""
ID: {s.id}
Telegram ID: {s.telegram_id}
Plan: {plan.name if plan else '❓ missing plan'}
Project: {project.name if project else '❓ missing project'}
Start: {s.start_at}
End: {s.end_at}
Status: {s.status}
--------------------------
        """)

def main():
    print("Connecting to DB...")
    db = SessionLocal()

    show_payments(db)
    show_subscriptions(db)

    db.close()

if __name__ == "__main__":
    main()
