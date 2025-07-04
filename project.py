import csv
import os
from tkinter import *
from tkinter import messagebox, ttk, simpledialog
import matplotlib.pyplot as plt
from collections import defaultdict

CSV_FILE = "inventory.csv"

# --------- CSV Functions ---------
def load_inventory():
    inventory = []
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name", "category", "quantity", "unit", "reorder_level", "price_per_unit"])
    with open(CSV_FILE, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['quantity'] = int(row['quantity'])
            row['reorder_level'] = int(row['reorder_level'])
            row['price_per_unit'] = float(row['price_per_unit'])
            inventory.append(row)
    return inventory

def save_inventory(inventory):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "category", "quantity", "unit", "reorder_level", "price_per_unit"])
        writer.writeheader()
        writer.writerows(inventory)

# --------- GUI Functions ---------
def refresh_tree(filtered_inventory=None):
    inventory = filtered_inventory if filtered_inventory else load_inventory()
    for row in tree.get_children():
        tree.delete(row)
    total_value = 0
    for item in inventory:
        total = item["quantity"] * item["price_per_unit"]
        total_value += total
        tree.insert("", END, values=(
            item["id"], item["name"], item["category"],
            item["quantity"], item["unit"],
            item["reorder_level"], f"{item['price_per_unit']:.2f}"
        ))
    total_value_label.config(text=f"Total Stock Value: ₹{total_value:.2f}")

def add_item():
    try:
        if not all([
            id_entry.get(), name_entry.get(), category_entry.get(),
            quantity_entry.get(), unit_entry.get(),
            reorder_entry.get(), price_entry.get()
        ]):
            messagebox.showerror("Error", "All fields are required.")
            return

        item = {
            "id": id_entry.get(),
            "name": name_entry.get(),
            "category": category_entry.get(),
            "quantity": int(quantity_entry.get()),
            "unit": unit_entry.get(),
            "reorder_level": int(reorder_entry.get()),
            "price_per_unit": float(price_entry.get())
        }

        inventory = load_inventory()
        inventory.append(item)
        save_inventory(inventory)
        refresh_tree()
        messagebox.showinfo("Success", "Item added.")

        for e in [id_entry, name_entry, category_entry, quantity_entry, unit_entry, reorder_entry, price_entry]:
            e.delete(0, END)

    except ValueError:
        messagebox.showerror("Error", "Enter valid numbers for quantity, reorder level, and price.")

def restock_item():
    item_id = simpledialog.askstring("Restock", "Enter Item ID to restock:")
    qty = simpledialog.askinteger("Restock", "Enter quantity to add:")
    inventory = load_inventory()
    for item in inventory:
        if item["id"] == item_id:
            item["quantity"] += qty
            save_inventory(inventory)
            refresh_tree()
            messagebox.showinfo("Success", f"{qty} added to {item['name']}.")
            return
    messagebox.showerror("Error", "Item not found.")

def sell_item():
    item_id = simpledialog.askstring("Sell", "Enter Item ID to sell:")
    qty = simpledialog.askinteger("Sell", "Enter quantity to sell:")
    inventory = load_inventory()
    for item in inventory:
        if item["id"] == item_id:
            if item["quantity"] >= qty:
                item["quantity"] -= qty
                save_inventory(inventory)
                refresh_tree()
                total = qty * item["price_per_unit"]
                messagebox.showinfo("Sold", f"Sold {qty} x {item['name']} for ₹{total:.2f}")
            else:
                messagebox.showerror("Error", "Not enough stock.")
            return
    messagebox.showerror("Error", "Item not found.")

def check_reorder():
    inventory = load_inventory()
    low_stock = [item for item in inventory if item["quantity"] <= item["reorder_level"]]
    if low_stock:
        msg = "\n".join(f"{item['name']} - {item['quantity']} {item['unit']} (Reorder: {item['reorder_level']})" for item in low_stock)
        messagebox.showwarning("Low Stock Items", msg)
    else:
        messagebox.showinfo("Good", "All items are sufficiently stocked.")

def edit_item():
    item_id = simpledialog.askstring("Edit Item", "Enter Item ID to edit:")
    inventory = load_inventory()
    for item in inventory:
        if item["id"] == item_id:
            new_name = simpledialog.askstring("Edit", f"Name ({item['name']}):") or item["name"]
            new_category = simpledialog.askstring("Edit", f"Category ({item['category']}):") or item["category"]
            new_qty = simpledialog.askinteger("Edit", f"Quantity ({item['quantity']}):") or item["quantity"]
            new_unit = simpledialog.askstring("Edit", f"Unit ({item['unit']}):") or item["unit"]
            new_reorder = simpledialog.askinteger("Edit", f"Reorder Level ({item['reorder_level']}):") or item["reorder_level"]
            new_price = simpledialog.askfloat("Edit", f"Price/Unit (₹{item['price_per_unit']}):") or item["price_per_unit"]
            item.update({"name": new_name, "category": new_category, "quantity": new_qty,
                         "unit": new_unit, "reorder_level": new_reorder, "price_per_unit": new_price})
            save_inventory(inventory)
            refresh_tree()
            messagebox.showinfo("Success", f"{item['name']} updated.")
            return
    messagebox.showerror("Error", "Item not found.")

def export_report():
    inventory = load_inventory()
    filename = "inventory_report.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Category", "Quantity", "Unit", "Reorder Level", "Price/Unit", "Total Value"])
        for item in inventory:
            total = item["quantity"] * item["price_per_unit"]
            writer.writerow([item["id"], item["name"], item["category"], item["quantity"], item["unit"], item["reorder_level"], item["price_per_unit"], total])
    messagebox.showinfo("Exported", f"Report saved as {filename}")

def filter_by_category():
    cat = category_filter.get().lower()
    inventory = load_inventory()
    filtered = [item for item in inventory if cat in item["category"].lower()]
    refresh_tree(filtered)

def show_stock_graph():
    inventory = load_inventory()
    category_totals = defaultdict(int)
    for item in inventory:
        category_totals[item['category']] += item['quantity']
    if not category_totals:
        messagebox.showinfo("No Data", "No items to show in chart.")
        return
    categories = list(category_totals.keys())
    quantities = list(category_totals.values())
    plt.figure(figsize=(8, 5))
    plt.bar(categories, quantities, color='skyblue')
    plt.title("Stock Quantity by Category")
    plt.xlabel("Category")
    plt.ylabel("Total Quantity")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# --------- GUI Setup ---------
root = Tk()
root.title("FreshMart Inventory Manager")

# Treeview
tree = ttk.Treeview(root, columns=("ID", "Name", "Category", "Qty", "Unit", "Reorder", "Price"), show="headings")
for col in tree["columns"]:
    tree.heading(col, text=col)
tree.grid(row=0, column=0, columnspan=8, padx=10, pady=10)

# Total Stock Value
total_value_label = Label(root, text="Total Stock Value: ₹0.00", font=("Arial", 12, "bold"))
total_value_label.grid(row=1, column=0, columnspan=8, pady=5)

# Search/filter
Label(root, text="Filter by Category:").grid(row=2, column=0)
category_filter = Entry(root)
category_filter.grid(row=2, column=1)
Button(root, text="Search", command=filter_by_category).grid(row=2, column=2)
Button(root, text="Show All", command=lambda: refresh_tree()).grid(row=2, column=3)

# Entry Fields
Label(root, text="ID").grid(row=3, column=0)
id_entry = Entry(root)
id_entry.grid(row=3, column=1)
Label(root, text="Name").grid(row=3, column=2)
name_entry = Entry(root)
name_entry.grid(row=3, column=3)
Label(root, text="Category").grid(row=3, column=4)
category_entry = Entry(root)
category_entry.grid(row=3, column=5)
Label(root, text="Quantity").grid(row=4, column=0)
quantity_entry = Entry(root)
quantity_entry.grid(row=4, column=1)
Label(root, text="Unit").grid(row=4, column=2)
unit_entry = Entry(root)
unit_entry.grid(row=4, column=3)
Label(root, text="Reorder Level").grid(row=4, column=4)
reorder_entry = Entry(root)
reorder_entry.grid(row=4, column=5)
Label(root, text="Price/Unit (₹)").grid(row=4, column=6)
price_entry = Entry(root)
price_entry.grid(row=4, column=7)

# Buttons
Button(root, text="Add Item", command=add_item).grid(row=5, column=0, pady=10)
Button(root, text="Edit Item", command=edit_item).grid(row=5, column=1)
Button(root, text="Restock", command=restock_item).grid(row=5, column=2)
Button(root, text="Sell", command=sell_item).grid(row=5, column=3)
Button(root, text="Check Low Stock", command=check_reorder).grid(row=5, column=4)
Button(root, text="Export Report", command=export_report).grid(row=5, column=5)
Button(root, text="Stock Graph", command=show_stock_graph).grid(row=5, column=6)
Button(root, text="Exit", command=root.destroy).grid(row=5, column=7)

refresh_tree()
root.mainloop()
