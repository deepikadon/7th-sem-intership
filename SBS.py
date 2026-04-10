from datetime import datetime, timedelta
import random
 
 
class User:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email
 
 
class Plan:
    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = price
 
 
class Subscription:
    def __init__(self, user_id, plan_id):
        self.user_id = user_id
        self.plan_id = plan_id
        self.next_billing = datetime.now() + timedelta(days=30)
        self.status = "Active"
 
 
class Invoice:
    def __init__(self, id, user_id, amount):
        self.id = id
        self.user_id = user_id
        self.amount = amount
        self.status = "Pending"
 
 
class SubscriptionSystem:
    PLANS = [
        Plan(1, "Free", 0),
        Plan(2, "Pro", 10),
        Plan(3, "Enterprise", 30),
    ]
 
    COUPONS = {
        "SAVE10": ("percent", 10),
        "SAVE20": ("percent", 20),
        "FLAT5":  ("flat",    5),
    }
 
    def __init__(self):
        self.users = []
        self.subscriptions = []
        self.invoices = []
        self._next_user_id = 1
        self._next_invoice_id = 1
 
    
 
    def _get_plan(self, plan_id):
        return next((p for p in self.PLANS if p.id == plan_id), None)
 
    def _get_user(self, user_id):
        return next((u for u in self.users if u.id == user_id), None)
 
    def _get_subscription(self, user_id):
        return next((s for s in self.subscriptions if s.user_id == user_id), None)
 
    def _show_plans(self):
        print("\nPlans:")
        for p in self.PLANS:
            print(f"  {p.id}. {p.name} — ${p.price}/mo")
 
    def _show_users(self):
        if not self.users:
            print("No users yet.")
            return
        for u in self.users:
            print(f"  {u.id}. {u.name} ({u.email})")
 
    
    def _apply_coupon(self, amount):
        code = input("Coupon code (or press Enter to skip): ").strip().upper()
        if not code:
            return amount
 
        if code not in self.COUPONS:
            print("Invalid coupon.")
            return amount
 
        kind, value = self.COUPONS[code]
        discount = (amount * value / 100) if kind == "percent" else value
        final = max(0, amount - discount)
        print(f"Coupon applied! Discount: ${discount:.2f}  Final: ${final:.2f}")
        return final
 
    def _charge(self, user_id, amount):
        invoice = Invoice(self._next_invoice_id, user_id, amount)
        self._next_invoice_id += 1
        self.invoices.append(invoice)
 
        for attempt in range(1, 4):
            print(f"Payment attempt {attempt}…")
            if random.choice([True, False]):
                invoice.status = "Paid"
                print("Payment successful.")
                return True
            print("Failed.")
 
        invoice.status = "Overdue"
        sub = self._get_subscription(user_id)
        if sub:
            sub.status = "Overdue"
        print("Payment overdue — subscription marked overdue.")
        return False
 
 
    def create_user(self):
        name = input("Name: ").strip()
        email = input("Email: ").strip()
        user = User(self._next_user_id, name, email)
        self.users.append(user)
        self._next_user_id += 1
        print(f"User #{user.id} created.")
 
    def subscribe(self):
        if not self.users:
            print("Create a user first.")
            return
 
        self._show_users()
        user = self._get_user(int(input("User ID: ")))
        if not user:
            print("User not found.")
            return
 
        if self._get_subscription(user.id):
            print("User already has a subscription.")
            return
 
        self._show_plans()
        plan = self._get_plan(int(input("Plan ID: ")))
        if not plan:
            print("Invalid plan.")
            return
 
        self.subscriptions.append(Subscription(user.id, plan.id))
        print(f"{user.name} subscribed to {plan.name}.")
 
        if plan.price > 0:
            amount = self._apply_coupon(plan.price)
            self._charge(user.id, amount)
 
    def change_plan(self):
        self._show_users()
        user = self._get_user(int(input("User ID: ")))
        if not user:
            print("User not found.")
            return
 
        sub = self._get_subscription(user.id)
        if not sub:
            print("No subscription found.")
            return
 
        self._show_plans()
        new_plan = self._get_plan(int(input("New plan ID: ")))
        if not new_plan:
            print("Invalid plan.")
            return
 
        if sub.plan_id == new_plan.id:
            print("Already on that plan.")
            return
 
        remaining = (sub.next_billing - datetime.now()).days
        prorated = round((remaining / 30) * new_plan.price, 2)
        sub.plan_id = new_plan.id
        print(f"Switched to {new_plan.name}. Prorated charge: ${prorated}")
 
        if prorated > 0:
            self._charge(user.id, prorated)
 
    def cancel(self):
        self._show_users()
        sub = self._get_subscription(int(input("User ID: ")))
        if sub:
            sub.status = "Cancelled"
            print("Subscription cancelled.")
        else:
            print("No subscription found.")
 
    def billing_cycle(self):
        print("\n— Billing cycle —")
        for sub in self.subscriptions:
            if sub.status != "Active":
                continue
            if datetime.now() >= sub.next_billing:
                plan = self._get_plan(sub.plan_id)
                if plan and plan.price > 0:
                    print(f"Charging user #{sub.user_id} for {plan.name}…")
                    self._charge(sub.user_id, plan.price)
                sub.next_billing += timedelta(days=30)
 
 
def main():
    system = SubscriptionSystem()
 
    menu = {
        "1": ("Create user",       system.create_user),
        "2": ("Subscribe to plan", system.subscribe),
        "3": ("Change plan",       system.change_plan),
        "4": ("Cancel subscription", system.cancel),
        "5": ("View users",        system._show_users),
        "6": ("Run billing cycle", system.billing_cycle),
        "7": ("Exit", None),
    }
 
    while True:
        print("\n===== Subscription System =====")
        for key, (label, _) in menu.items():
            print(f"  {key}. {label}")
 
        choice = input("Choice: ").strip()
        if choice == "7":
            break
        action = menu.get(choice, (None, None))[1]
        if action:
            action()
        else:
            print("Invalid choice.")
 
 
if __name__ == "__main__":
    main()